from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_community.vectorstores import Qdrant
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PDFMinerLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.retrieval_qa.base import RetrievalQA
import os
import re
import json


class ResumeAnalyzer:
    def __init__(self, google_api_key, collection_name, qdrant_host="localhost", qdrant_port=6333):
        self.google_api_key = google_api_key
        self.qdrant_host = qdrant_host
        self.qdrant_port = qdrant_port
        self.qdrant_client = QdrantClient(host=self.qdrant_host, port=self.qdrant_port)
        self.collection_name = collection_name
        self.setup_qdrant()
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=self.google_api_key
        )
        self.vectorstore = Qdrant(
            client=self.qdrant_client,
            collection_name=self.collection_name,
            embeddings=self.embeddings
        )
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=self.google_api_key,
            model='gemini-1.5-flash',  # Use your preferred model
            temperature=0.1,
            top_p=0.95,
            convert_system_message_to_human=True
        )
        self.qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever()
        )
        self.query = """
                        Analise o currículo como se fosse um recrutador de uma seleção de emprego.
                        A saida deve ser um dicionario com as seguintes keys:
                        - nome
                        - email
                        - sexo: Apenas o sexo do candidato, sem comentarios no texto
                        - cargo: Um cargo é um nome ou designação dado a um cargo ou posição.
                        O título pode descrever a ocupação, cargo ou função da pessoa que ocupa o cargo, ou pode ser um termo de marketing usado para descrever o produto ou serviço.
                        - competências: Extrair uma lista com as competências do candidato
                        - perfil: Trace um perfil do candidato
                     """

    def setup_qdrant(self):
        self.qdrant_client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )

    def get_chunks(self, text):
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        return chunks

    def analyze_resume(self, resume_path, output_dir='../cv_json'):
        loader = PDFMinerLoader(file_path=resume_path)
        documents = loader.load()
        if documents:
            document_object = documents[0]
            page_content = document_object.page_content
            texts = self.get_chunks(page_content)
            self.vectorstore.add_texts(texts)

            try:
                response = self.qa.run(self.query)
                conteudo = re.search(r"```json(.*?)```", response, re.DOTALL).group(1)
                dicionario = json.loads(conteudo)

                os.makedirs(output_dir, exist_ok=True)
                with open(f'{output_dir}/{dicionario["nome"]}.json', 'w') as fp:
                    json.dump(dicionario, fp)
            except AttributeError as e:
                print(f"Error extracting data from resume: {resume_path}. Error: {e}")
                # Handle the error, e.g., log it or skip the file
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON data from resume: {resume_path}. Error: {e}")
                # Handle the error, e.g., log it or skip the file
        else:
            print(f"Error loading resume from: {resume_path}")