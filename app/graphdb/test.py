from typing import Optional, List, Dict, Union

def create_cypher(json_text: Dict[str, Union[str, List[str]]]) -> str:
    # Start the Cypher query
    query = "MATCH (p:Person) WHERE "
    conditions = []

    # Add role filtering
    role = json_text.get("role")
    if role:
        if isinstance(role, list):
            role_condition = " OR ".join([f"'{r}' IN p.role" for r in role])
            conditions.append(f"({role_condition})")
        elif isinstance(role, str):
            conditions.append(f"p.role = '{role}'")

    # Add skill filtering
    skill = json_text.get("skill")
    if skill:
        if isinstance(skill, list):
            skill_condition = " OR ".join([f"'{sk}' IN p.skill" for sk in skill])
            conditions.append(f"({skill_condition})")
        elif isinstance(skill, str):
            conditions.append(f"'{skill}' IN p.skill")

    # Add certification filtering
    certification = json_text.get("certification")
    if certification:
        if isinstance(certification, list):
            cert_condition = " OR ".join([f"'{cert}' IN p.certification" for cert in certification])
            conditions.append(f"({cert_condition})")
        elif isinstance(certification, str):
            conditions.append(f"'{certification}' IN p.certification")

    # Add education degree filtering
    education_degree = json_text.get("education_degree")
    if education_degree:
        if isinstance(education_degree, list):
            degree_condition = " OR ".join([f"'{deg}' IN p.education_degree" for deg in education_degree])
            conditions.append(f"({degree_condition})")
        elif isinstance(education_degree, str):
            conditions.append(f"p.education_degree = '{education_degree}'")

    # Combine all conditions into the query
    if conditions:
        query += " AND ".join(conditions)
    else:
        query = query.rstrip(" WHERE ")

    # Complete the Cypher query
    query += " RETURN p"

    return query

if __name__ == "__main__":
    description = {
    "role": "AI Engineer",
    "skill": ["Machine Learning", "Computer Vision"],
    "certification": "",
    "education_degree": "Bachelor"
}

    print(create_cypher(description))
