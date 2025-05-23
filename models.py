from pydantic import BaseModel, Field
from typing import List


class Character(BaseModel):
    name: str = Field(
        description="Name of the character from the book"
    )
    
    role: str = Field(
        description="A single or two word description of the characters role in the book"
    )
    
    description: str  =Field(
        description="A short description of the character which shows high level details about the character"
    )
    
    bio: str = Field(
        description="A deep explaination about the character and relationship with other people, personality traits, overall theme"
    )
    
    traits: list[str] = Field(
        description="A list of character traits in the book, eg: [Thoughtful, Regretful, Curious, Resilient, Introspective]"
    )
    
class Quotes(BaseModel):
    quotes : list[str] = Field(
        description="A list of quotes the character has said in the book that are very important to the character and the reader"
    )

class QueryStructure(BaseModel):
    Task: str = Field(
        description="Task to explicity specific what we are looking for eg: 'Direct Quotations spoken by ...'"
    )
    
    Target: str = Field(
        description="Name of the character"
    )
    
    Aliases: str = Field(
        description="Aliases of the character if they go by a different name, if any."
    )
    
    Qualities: str = Field(
        description="Qualities of the character to be used to create a solid query"
    )
    
    Exclude: str = Field(
        description="Rules that say to exclude some stuff"
    )
    
    OutFormat: str = Field(
        description= "Explain stuff about the kind of results, eg: 'passage verbatim (no commentary)'"
    )  

class Relation(BaseModel):
    name: str = Field(
        description="Name of the character who our character has this particular relation to"
    )
    relation: str = Field(
        description="A one or two word description of the relation to our charcter this character"
    )
    description: str = Field(
        description="A two sentence description of the relationship between our character and this character in the book"
    )

class Relations(BaseModel):
    relations: List[Relation] = Field(
        description="A list of important relationships the character of intersted has with other characters in the book"
    )

class ArcEntry(BaseModel):
    title: str = Field(
        description="A one or two word description of an entry that describes arc of the character egs: Despair, Exploration, Understanding"
    )
    
    description: str = Field(
        description="Description of the arc entry egs: At the beginning of the story, Nora is in a state of deep despair, feeling that her life has been a series of disappointments and that she has let everyone down."
    )

class CharacterArcs(BaseModel):
    arcs: list[ArcEntry] = Field(
        description="An ordererd list from top to bottom that shows how the character progresses in the list of arcs"
    )

class FinalCharacter(Character):
    quotes: Quotes
    relationships: Relations
    arcs: CharacterArcs


class Character(BaseModel):
    name: str = Field(
        description="Name of the character from the book"
    )
    
    role: str = Field(
        description="A single or two word description of the characters role in the book"
    )
    
    description: str  =Field(
        description="A short description of the character which shows high level details about the character"
    )
    
    bio: str = Field(
        description="A deep explaination about the character and relationship with other people, personality traits, overall theme"
    )
    
    traits: list[str] = Field(
        description="A list of character traits in the book, eg: [Thoughtful, Regretful, Curious, Resilient, Introspective]"
    )

class Characters(BaseModel):
    characters: List[Character] = Field(
        description="A list of major characters from the book who should be worth noted"
    )
