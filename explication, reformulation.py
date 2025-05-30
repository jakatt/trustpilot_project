import argparse
import os
import pandas as pd
from tqdm import tqdm
import openai
from dotenv import load_dotenv
import PyPDF2

def extract_pdf_text(pdf_path):
    """Extract all text from a PDF file."""
    text = ""
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def build_prompt(row, guidelines_text):
    """
    Construit le prompt à envoyer à OpenAI pour une plainte donnée, en se basant uniquement sur les guidelines Trustpilot.
    """
    prompt = f"""
Voici les informations d'une plainte utilisateur suite au retrait de son avis sur Trustpilot :

ID : {row['ID']}
Nom de la société : {row['Company Name']}
Nom de l'utilisateur : {row['User Name']}
Avis détaillé : {row['Detailed Review']}
Raison du retrait (Trustpilot) : {row['Reason for Removal']}
Note de l'avis : {row['Star Rating']}
Commentaire de la société : {row['Company Comment']}

Voici les guidelines officielles Trustpilot :
{guidelines_text}

1. En te référant aux guidelines et à toutes les informations ci-dessus, explique à l'utilisateur pourquoi son avis a été supprimé.
2. Propose une reformulation conforme aux guidelines et aux autres informations de la ligne, afin d'éviter tout problème de suppression.

Présente la réponse sous la forme :
Explication : ...
Nouvelle formulation : ...
"""
    return prompt

import glob

def main():
    cwd = os.getcwd()
    # Charger la clé API depuis setvar.env
    load_dotenv(dotenv_path=os.path.join(cwd, 'setvar.env'))
    # Recherche du fichier Excel 'Trustpilot_Dataset.xlsx'
    excel_path = os.path.join(cwd, 'Trustpilot_Dataset.xlsx')
    if not os.path.isfile(excel_path):
        raise FileNotFoundError("Le fichier 'Trustpilot_Dataset.xlsx' est introuvable dans le répertoire courant.")
    print(f"Fichier Excel utilisé : {os.path.basename(excel_path)}")

    # Recherche du PDF trustpilot_guidelines.pdf
    guidelines_path = os.path.join(cwd, 'trustpilot_guidelines.pdf')
    if not os.path.isfile(guidelines_path):
        raise FileNotFoundError("Le fichier 'trustpilot_guidelines.pdf' est introuvable dans le répertoire courant.")
    print(f"PDF des guidelines utilisé : {os.path.basename(guidelines_path)}")

    output_path = os.path.join(cwd, 'output_trustpilot.xlsx')

    # Extraction du texte des guidelines
    print("Extraction du texte des guidelines...")
    guidelines_text = extract_pdf_text(guidelines_path)

    # Lecture du fichier Excel, feuille 'dataset'
    try:
        df = pd.read_excel(excel_path, sheet_name='dataset')
    except ValueError:
        raise ValueError("La feuille 'dataset' est introuvable dans le fichier Excel.")
    results = []

    # Récupération de la clé API
    openai.api_key = os.getenv('OPENAI_API_KEY')
    if openai.api_key is None:
        raise RuntimeError("Clé API OpenAI manquante. Ajoutez-la dans un fichier .env sous la forme OPENAI_API_KEY=sk-...")

    for idx, row in tqdm(df.iterrows(), total=len(df)):
        prompt = build_prompt(row, guidelines_text)
        try:
            response = openai.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.3
            )
            output = response.choices[0].message.content.strip()
            # Séparation explication / reformulation
            explication = ""
            reformulation = ""
            if "Nouvelle formulation :" in output:
                parts = output.split("Nouvelle formulation :", 1)
                explication = parts[0].replace("Explication :", "").strip()
                reformulation = parts[1].strip()
            else:
                explication = output
            result_dict = row.to_dict()
            result_dict["Explication"] = explication
            result_dict["Nouvelle formulation"] = reformulation
            results.append(result_dict)
        except Exception as e:
            result_dict = row.to_dict()
            result_dict["Explication"] = f"Erreur OpenAI: {e}"
            result_dict["Nouvelle formulation"] = ""
            results.append(result_dict)
    # Sauvegarde
    out_df = pd.DataFrame(results)
    out_df.to_excel(output_path, index=False)
    print(f"Fichier de sortie généré : {output_path}")

if __name__ == "__main__":
    main()
