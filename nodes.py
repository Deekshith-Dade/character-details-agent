from states import QuotesAgentState, QuotesAgentStateOutput, RelationsAgentState, RelationsAgentStateOutput, CharacterArcAgentState, CharacterArcAgentStateOutput, CharacterDetailState, CollectorDetailState, CharacterDetailStateOutput, GenerateCharacterState, GenerateCharacterStateOutput
from models import Character, CharacterArcs, FinalCharacter, Quotes, Relations, QueryStructure, Characters
from prompts import rag_prompt, quote_writer_prompt, relations_generator_prompt, character_arc_prompt, charactermaker_instructions
from models_init import llm, embedder, pc

from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.constants import Send

def rag_query_writer(state: QuotesAgentState):
    character = state['curr_character']
    
    system_message = rag_prompt.format(name=character.name,
                                       role=character.role,
                                       description=character.description,
                                       bio=character.bio)
    query_llm = llm.with_structured_output(QueryStructure)
    response = query_llm.invoke([SystemMessage(content=system_message)] + [HumanMessage(content="Now produce query for the rag search")])
    return {"rag_query": response}

def rag_tool(state: QuotesAgentState):
    rag_query = state['rag_query']
    index_name = state['index_name']
    top_k = state['rag_top_k']
    
    query = f"""
    Task: {rag_query.Task}
    Target: {rag_query.Target}
    Aliases: {rag_query.Aliases}
    Desired Qualities: {rag_query.Qualities}
    Exclude: {rag_query.Exclude}
    Output Format: {rag_query.OutFormat}
    """
    
    try:
        index = pc.Index(index_name)
        query_embedding = embedder.embed_query(query)
        
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        context = ""
        for match in results['matches']:
            context += f"Content: {match['metadata']['text']}\n\n"
        
        return {"additional_context" : context}
    except:
        print(f"Error getting RAG context")
        return {"additional_context" : "No Context"}

def quote_writer(state: QuotesAgentState) -> QuotesAgentStateOutput:
    character = state['curr_character']
    additional_context = state['additional_context']
    
    system_message = quote_writer_prompt.format(character_name=character.name,
                                         additional_context=additional_context)
    
    quotes_llm = llm.with_structured_output(Quotes)
    response = quotes_llm.invoke([SystemMessage(content=system_message)] + [HumanMessage(content="Now fetch high qualty and intersting quotes from the character")])
    return {"quotes": Quotes(quotes=response.quotes)}

def relationship_generator(state: RelationsAgentState) -> RelationsAgentStateOutput:
    characters = state['characters']
    character = state['curr_character']
    chapter_summaries = state['chapter_summaries']
    max_relations = state['max_relations']
    
    character_context = ""
    counter = 1
    for c in characters:
        if c.name != character.name:
            character_context += f"""Character {counter}
            Name: {character.name}
            Role: {character.role}
            Description: {character.description}/n/n
            """ 
            counter = counter + 1
    
    system_prompt = relations_generator_prompt.format(character_name=character.name,
                                                      character_description=character.description,
                                                      character_context=character,
                                                      chapter_summaries=chapter_summaries,
                                                      max_relations=max_relations)
    relations_llm = llm.with_structured_output(Relations) 
    response = relations_llm.invoke([SystemMessage(content=system_prompt) , HumanMessage(content="Create the relationship details")])
    
    return {"relations": Relations(relations=response.relations)}

def character_arc_generator(state: CharacterArcAgentState) -> CharacterArcAgentStateOutput:
    character = state['curr_character']
    chapter_summaries = state['chapter_summaries']
    max_arcs = state['max_arcs']
    
    system_message = character_arc_prompt.format(character_name=character.name,
                                                 character_description=character.description,
                                                 chapter_summaries=chapter_summaries,
                                                 max_arcs=max_arcs)
    
    arcs_llm = llm.with_structured_output(CharacterArcs)
    response = arcs_llm.invoke([SystemMessage(content=system_message)])
    
    return {"character_arcs": CharacterArcs(arcs=response.arcs)}

def initiator(state: CharacterDetailState):
    
    changes = {
        "index_name": state['index_name'],
        "rag_top_k": state['rag_top_k'],
        "max_arcs": state['max_arcs'],
        "max_relations": state['max_relations'],
    }
    
    return changes

def collector(state: CollectorDetailState) -> CharacterDetailStateOutput:
    curr_character = state['curr_character']
    base_fields = curr_character.model_dump()

    final_character = FinalCharacter(
        **base_fields,
        quotes=state.get("quotes", Quotes(quotes=[])),
        relationships=state.get("relations", Relations(relations=[])),
        arcs=state.get("character_arcs", CharacterArcs(arcs=[])),
    )
    
    return {"final_characters": [final_character]}

def create_characters(state: GenerateCharacterState):
    """Generate Characters"""
    book_name = state['book_name']
    max_characters = state['max_characters']
    chapters_context = state['chapter_summaries']
    human_feedback = state['feedback']
    
    structured_llm = llm.with_structured_output(Characters)
    
    system_message = charactermaker_instructions.format(book_name=book_name,
                                                        max_characters=max_characters,
                                                        chapters_context=chapters_context,
                                                        human_feedback=human_feedback)
    characters = structured_llm.invoke([SystemMessage(content=system_message)] + [HumanMessage(content="Generate the set of characters.")])
    
    return {"characters": characters.characters}

def human_feedback(state: GenerateCharacterState):
    """ No-op node that should be interrupted on """
    pass


def should_continue(state: GenerateCharacterState):
    """ Return the next node to execute """

    # Check if human feedback
    feedback = state.get('feedback', None)
    if feedback:
        return "create_characters"
    else:
        print("Current Characters " ,len(state["characters"]))
        return [Send("character_details", {
            "curr_character": character,
            "characters": state["characters"],
            "chapter_summaries": state["chapter_summaries"],
            "index_name": state["index_name"],
            "rag_top_k": state["rag_top_k"],
            "max_arcs": state["max_arcs"],
            "max_relations": state["max_relations"],
        }) for character in state["characters"]]
        
def sink_node(state: GenerateCharacterState) -> GenerateCharacterStateOutput :
    pass