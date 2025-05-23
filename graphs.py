from nodes import (
    rag_query_writer,
    rag_tool,
    quote_writer,
    relationship_generator,
    character_arc_generator,
    initiator,
    collector,
)

from nodes import (
    create_characters,
    human_feedback,
    should_continue,
    sink_node
)
from states import (QuotesAgentState, QuotesAgentStateOutput, 
                    RelationsAgentState, RelationsAgentStateOutput,
                    CharacterArcAgentState, CharacterArcAgentStateOutput,
                    CharacterDetailState, CharacterDetailStateOutput,
                    GenerateCharacterState, GenerateCharacterStateOutput)

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.memory import MemorySaver

class QuoteWriterGraph:
    def __init__(self):
        pass
    
    def build(self):
        quote_writer_builder = StateGraph(QuotesAgentState, QuotesAgentStateOutput)
        quote_writer_builder.add_node("rag_query_writer", rag_query_writer)
        quote_writer_builder.add_node("rag_tool", rag_tool)
        quote_writer_builder.add_node("quote_writer", quote_writer)

        quote_writer_builder.add_edge(START ,"rag_query_writer")
        quote_writer_builder.add_edge("rag_query_writer", "rag_tool")
        quote_writer_builder.add_edge("rag_tool", "quote_writer")
        quote_writer_builder.add_edge("quote_writer", END)
        
        return quote_writer_builder
    
class RelationsGraph:
    def __init__(self):
        pass
    
    def build(self):
        relationship_builder = StateGraph(RelationsAgentState, output=RelationsAgentStateOutput)
        relationship_builder.add_node("relationship_generator", relationship_generator)
        relationship_builder.add_edge(START, "relationship_generator")
        relationship_builder.add_edge("relationship_generator", END)
        
        return relationship_builder


class CharacterArcGraph:
    def __init__(self):
        pass
    
    def build(self):
        character_arc_builder = StateGraph(CharacterArcAgentState, output=CharacterArcAgentStateOutput)
        character_arc_builder.add_node("character_arc_generator", character_arc_generator)
        character_arc_builder.add_edge(START, "character_arc_generator")
        character_arc_builder.add_edge("character_arc_generator", END)
        
        return character_arc_builder
        

class CharacterDetailGraph:
    def __init__(self):
        self.quote_writer_builder = QuoteWriterGraph().build()
        self.relationship_builder = RelationsGraph().build()
        self.character_arc_builder = CharacterArcGraph().build()
        self._graph: CompiledStateGraph = self.build()
    
    def build(self):
        character_det_builder = StateGraph(CharacterDetailState, output=CharacterDetailStateOutput)

        character_det_builder.add_node("initiator", initiator)
        character_det_builder.add_node("quoteAgent", self.quote_writer_builder.compile())
        character_det_builder.add_node("relationshipAgent", self.relationship_builder.compile())
        character_det_builder.add_node("characterarcAgent", self.character_arc_builder.compile())
        character_det_builder.add_node("collector", collector)


        character_det_builder.add_edge(START, "initiator")
        character_det_builder.add_edge("initiator", "quoteAgent")
        character_det_builder.add_edge("initiator", "relationshipAgent")
        character_det_builder.add_edge("initiator", "characterarcAgent")

        character_det_builder.add_edge( ["quoteAgent", "relationshipAgent", "characterarcAgent"], "collector")
        character_det_builder.add_edge( "collector",END)
        
        return character_det_builder
    
class CharacterMakerGraph:
    def __init__(self):
        self.character_detail_builder = CharacterDetailGraph().build()
        self._graph: CompiledStateGraph = self.build()
    
    def build(self):
        builder = StateGraph(GenerateCharacterState, output=GenerateCharacterStateOutput)
        builder.add_node("create_characters", create_characters)
        builder.add_node("human_feedback", human_feedback)
        builder.add_node("character_details", self.character_detail_builder.compile())
        builder.add_node("sink_node", sink_node)


        builder.add_edge(START, "create_characters")
        builder.add_edge("create_characters", "human_feedback")
        builder.add_conditional_edges("human_feedback", should_continue, ["create_characters", "character_details"])
        builder.add_edge("character_details", "sink_node")
        builder.add_edge("sink_node", END)

        
        return builder