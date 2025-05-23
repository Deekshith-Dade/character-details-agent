from graphs import CharacterMakerGraph
from preprocess import preprocess
from dotenv import load_dotenv
from typing import Optional
from rich import print
import json
from tqdm import tqdm
from langgraph.checkpoint.memory import MemorySaver



load_dotenv()

def interactive_run(
    graph,
    book_name: str,
    chapter_summaries: str,
    index_name: str,
    rag_top_k: int,
    max_arcs: int,
    max_relations: int,
    max_characters: int,
    thread_id: str = "1",
):
    # ---- 1. initialise the run ----
    root_state = {
        "book_name": book_name,
        "chapter_summaries": chapter_summaries,
        "index_name": index_name,
        "rag_top_k": rag_top_k,
        "max_arcs": max_arcs,
        "max_relations": max_relations,
        "max_characters": max_characters,
        "feedback": None,
    }
    thread = {"configurable": {"thread_id": thread_id}}

    # we'll call graph.stream() repeatedly, passing `None` after the first tick
    pending_state: Optional[dict] = root_state
    done = False

    while not done:
        for event in graph.stream(pending_state, thread, stream_mode="values"):
            pass
        
        state = graph.get_state(thread)
        next_nodes = state.next
        if "human_feedback" in next_nodes:
            chars = state.values["characters"]
            print("\n[bold]Characters:[/bold]")
            for i, c in enumerate(chars, 1):
                print(f"{i}. {c.name} — {c.role}")
                
            fb = input(
                "\nEnter feedback (blank ↵ to approve & continue): "
            ).strip() or None
            
            graph.update_state(thread, {"feedback": fb}, as_node="human_feedback")
            
            pending_state = None
            continue
        
        done = True
    
    final_state = graph.get_state(thread)
    return final_state.values["final_characters"]

def main():
    epub_path = "books/files/karamazov.epub"
    index_name, details_file_path = preprocess(epub_path)
    
    charactermaker_builder = CharacterMakerGraph().build()
    memory = MemorySaver()
    graph = charactermaker_builder.compile(interrupt_before=["human_feedback"],checkpointer=memory)
    graph.get_graph(xray=1).draw_mermaid_png(output_file_path="character_maker_graph.png")
    
    book_name = "The Origin of Species"
    
    with open(f"{details_file_path}/chapter_details.json", "r") as f:
        chapters = json.load(f)
    
    chapter_summaries = ""
    for chapter in tqdm(chapters, desc="Processing chapters"):
        summary = chapter.get("summary", None)
        if summary:
            chapter_summaries += f"{summary}\n\n"
    print("Chapter Summary Length: ", len(chapter_summaries))
    final_characters = interactive_run(graph, 
                                       book_name, 
                                       chapter_summaries, 
                                       index_name, 
                                       rag_top_k=5, 
                                       max_arcs=8, 
                                       max_relations=8, 
                                       max_characters=10)
    final_characters_json = [c.model_dump() for c in final_characters]
    with open(f"{details_file_path}/final_characters.json", "w") as f:
        json.dump(final_characters_json, f)


if __name__ == "__main__":
    print("Starting character-details...")
    main()
