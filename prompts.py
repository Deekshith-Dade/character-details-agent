# Prompts
summary_prompt = """
You are a helpful assistant. Summarize the following in 5-6 sentences. 
Focus on key events, emotional beats, and characters.

I will tell you exactly what is happening here. I'm trying to get the summaries of the chapters.

I'm doing all this to get details about characters in the books like their peers, their role, trajectory of their plot.

The summary should be tight and high signal that the model which picks up this summary should understand exactly what's going.

You don't even need to write this in plain english only high signal

So make sure you convey the right information needed which I can process later for downstream usage for character understanding.

Chapter:
{text}
"""

character_prompt = """You are a helpful assistant, who understands the given context and identifies the relevant characters from the book.

Follow these instructons

1. Do your best to get the character and understand his role in the text

2. The context
{text}
"""

rag_prompt = """You are an expert at writing relevant query to get hits from the RAG Search operation

1. Your task is to given the character details understand the character based on name, role, description and bio.

Character: 
Name: {name}
Role: {role}
Description: {description}
Bio: {bio}

2. The goal Now is to fetch quotes that this character has said from the book
3. The query you provide will be used to queried to get relevant documents to constuct the character profile
4. These documents will be used to produce exact quotes that this character has said.

Produce the Query now.
"""

quote_writer_prompt = """You are an expert literary analyst and quotation extractor.

Goal  
• Produce a clean list of direct quotations spoken by the character {character_name}.
• Each quote must be exactly as it appears in the source passage, including punctuation.

Strict Criteria  
1. The quoted text is inside quotation marks in the source.  
2. The speaker is unambiguously the target character (or a pronoun that clearly refers to them).  
3. Keep each quote ≤ 2 sentences and self-contained (readable without extra context).  
4. Eliminate duplicates or near-duplicates.  
5. Return **5-8** of the strongest quotes; if fewer qualify, return what you have. Produce evne number of quotes
6. Only include quotes that will be interested to look at, don't include mundane conversation stuff.
Context:
{additional_context}
"""

relations_generator_prompt = """You are a literary maestro, super logical person who can weave through stories and find connections.

Your task is to find relationships between the characters from the book. 

You will be given characters and the details and the summary of each chapter of the book, you absorb it completely with your prowess.

You will then produce these relations and description between the relationships between the character of intersted and other characters.

In this case our character of interest is {character_name}, who is described as {character_description}.

Characters from the book

{character_context}

Summary of the whole book

{chapter_summaries}

Find at most {max_relations} relations in the format specified.
"""

character_arc_prompt = """You are a literary maestro, super logical person who can weave through stories and find connections.

Your task is to find character arc from the book. 

You will be given  the summary of each chapter of the book, you absorb it completely with your prowess.

You will then produce these relevant titles and descriptions of the character arcs.

You will make sure the character arcs flow in order to produce an interesting narrative of the character.

In this case our character of interest is {character_name}, who is described as {character_description}.

Summary of the whole book

{chapter_summaries}

Do not use your general knowledge about the book, only what's provided.

Find at most {max_arcs} character arcs to make a fascinating narrative in the format specified.
"""

charactermaker_instructions="""You are tasked with creating a set of Characters from the book {book_name}. Follow these instructions carefully.

1. First review the book using the context provided from the summaries of each chapter.
{chapters_context}

2. Examine the most important character you think are often recurring and intersting, serve the plot and pick only top {max_characters}

3. Determine characters and infer their small desription, a big biography of them from the book.

4. Never spoil what happens to the character, if you're unsure about including certain scenes because they spoil the plot, don't mention it.

5. Assign roles based on your understanding of the character.

6. If there is any human feedback incorporate it Human Feedback: {human_feedback}
"""
