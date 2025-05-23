from typing_extensions import TypedDict, Annotated
from models import Character, CharacterArcs, FinalCharacter, Quotes, Relations, QueryStructure
from typing import List
import operator


# Agent States
class QuotesAgentState(TypedDict):
    curr_character: Character
    additional_context: list[str]
    rag_query: QueryStructure
    quotes: Quotes
    index_name: str 
    rag_top_k: int

class QuotesAgentStateOutput(TypedDict):
    quotes: Quotes

class RelationsAgentState(TypedDict):
    curr_character: Character
    characters: List[Character]
    chapter_summaries: str
    max_relations: int
    relations: Relations

class RelationsAgentStateOutput(TypedDict):
    relations: Relations

class CharacterArcAgentState(TypedDict):
    curr_character: Character
    chapter_summaries: str
    max_arcs: int 
    character_arcs: CharacterArcs
    
class CharacterArcAgentStateOutput(TypedDict):
    character_arcs: CharacterArcs

class CollectorDetailState(TypedDict):
    curr_character: Character
    quotes: Quotes
    relations: Relations
    character_arcs: CharacterArcs
    final_characters: Annotated[List[FinalCharacter], operator.add]

#  Character Detail Agent State
class CharacterDetailState(TypedDict):
    curr_character: Character
    characters: List[Character]
    chapter_summaries: str
    
    final_characters: Annotated[List[FinalCharacter], operator.add]
    
    quotes: Quotes
    relations: Relations
    character_arcs: CharacterArcs
    
    index_name: str 
    rag_top_k: int
    max_arcs: int
    max_relations: int
    
class CharacterDetailStateOutput(TypedDict):
    final_characters: Annotated[List[FinalCharacter], operator.add]
    

#  Main Agent State
class GenerateCharacterState(TypedDict):
    book_name: str
    chapter_summaries: str
    max_characters: int
    feedback: str
    characters: List[Character]
    final_characters: Annotated[List[FinalCharacter], operator.add]
    
    index_name: str
    rag_top_k: int
    max_arcs: int
    max_relations: int
    
class GenerateCharacterStateOutput(TypedDict):
    final_characters: Annotated[List[FinalCharacter], operator.add]
   