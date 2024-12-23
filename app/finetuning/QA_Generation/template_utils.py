from langchain_core.prompts import ChatPromptTemplate


def categories_template() -> ChatPromptTemplate:
    template = ChatPromptTemplate.from_messages([
        ("system", "You are an English-speaking recruiter"),
        ("human", "Please suggest {n_category} distinct domains together and do not contain example.\n\n"
                  "Example result:\n\n"
                  "\"category\": \"Artificial Intelligence\"")
        ])
    return template


def generate_Q_template() -> ChatPromptTemplate:
    template = ChatPromptTemplate.from_messages([
        ("system", 
            "You are an English-speaking recruiter."
        ),
        ("human", 
            "You should create query corresponding to each JSON resume in the provided list. "
            "Each created query (natural language) that must contain all values of each JSON resume. "
            "You should use synonyms for the values in these keys: role, skill, certification, and education_degree to make the query more diverse.\n\n"
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
            "Create {n_pair} variations of resumes specifically tailored for different types of roles within the {category} domain.\n"
            "The role, skill, certification, education_degree should match an entry in the list."
        )
    ])
    return template
