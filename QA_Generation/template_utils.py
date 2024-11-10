from langchain_core.prompts import ChatPromptTemplate


def categories_template() -> ChatPromptTemplate:
    template = ChatPromptTemplate.from_messages([
        ("system", "You are an English-speaking recruiter"),
        ("human", "Please suggest {n_category} distinct domains together with their short descriptions and do not contain example.\n\n"
         "Here are some examples of the questions to be generated:\n\n"
            "\"category\": \"Artificial Intelligence\"\n\n"
         "")
        ])
    return template


def generate_Q_template() -> ChatPromptTemplate:
    template = ChatPromptTemplate.from_messages([
        ("system", 
            "You are an English-speaking recruiter."
        ),
        ("human", 
            "You should create query corresponding to each JSON resume in the provided list. "
            "Each created query (natural language) that must contain all values of each JSON resume.\n\n"
            "Here is the list of JSON resume:\n\n"
            "{answers}"
        )
    ])
    return template


def generate_A_template() -> ChatPromptTemplate:
    template = ChatPromptTemplate.from_messages([
        ("system", 
            "You are an English-speaking recruiter."
        ),
        ("human", 
            "Generate {n_pair} variations of resumes specifically tailored for different types of roles within the {category} domain"
        )
    ])
    return template
