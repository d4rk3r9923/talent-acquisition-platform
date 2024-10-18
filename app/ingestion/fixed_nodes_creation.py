import csv
import uuid
from app.preprocessing.fixed_schema import (
    list_universites,
    list_workplaces,
    list_positions,
    list_skills,
    list_certifications,
    list_publications
)
from dotenv import load_dotenv
load_dotenv()

def generate_uuid(value):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, value))

def write_csv(file_name, data_list, headers):
    with open(file_name, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data_list)

def prepare_nodes():
    university_nodes = [
        {"id": generate_uuid(uni.name), "name": uni.name, "field": uni.field}
        for uni in list_universites
    ]
    
    workplace_nodes = [
        {"id": generate_uuid(wp.name), "name": wp.name, "domain_expertise": wp.domain_expertise, "size": wp.size}
        for wp in list_workplaces
    ]
    
    position_nodes = [
        {"id": generate_uuid(pos.name), "name": pos.name, "description": pos.description}
        for pos in list_positions
    ]
    
    skill_nodes = [
        {"id": generate_uuid(skill.name), "name": skill.name, "category": skill.category}
        for skill in list_skills
    ]
    
    certification_nodes = [
        {"id": generate_uuid(cert.category), "category": cert.category}
        for cert in list_certifications
    ]
    
    publication_nodes = [
        {"id": generate_uuid(pub.category), "category": pub.category}
        for pub in list_publications
    ]
    
    return university_nodes, workplace_nodes, position_nodes, skill_nodes, certification_nodes, publication_nodes

def save_to_csv():
    university_nodes, workplace_nodes, position_nodes, skill_nodes, certification_nodes, publication_nodes = prepare_nodes()
    
    write_csv("universities.csv", university_nodes, ["id", "name", "field"])
    write_csv("workplaces.csv", workplace_nodes, ["id", "name", "domain_expertise", "size"])
    write_csv("positions.csv", position_nodes, ["id", "name", "description"])
    write_csv("skills.csv", skill_nodes, ["id", "name", "category"])
    write_csv("certifications.csv", certification_nodes, ["id", "category"])
    write_csv("publications.csv", publication_nodes, ["id", "category"])

def to_db():
    # to_do: write cypher to up to the database
