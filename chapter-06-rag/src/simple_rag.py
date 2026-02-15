import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI  # Assuming you have API key set

client = chromadb.PersistentClient(path="./chroma_db")
emb_fn = embedding_functions.DefaultEmbeddingFunction()
collection = client.get_collection(name="driver_policy", embedding_function=emb_fn)

llm_client = OpenAI()

def ask_rag(question):
    print(f"\nUser Question: {question}")
    
    # 1. Retrieve (Get top 2 most relevant chunks)
    results = collection.query(query_texts=[question], n_results=2)
    context_text = "\n\n".join(results['documents'][0])
    
    print(f"--- Retrieved Context ---\n{context_text}\n-------------------------")
    
    # 2. Augment (Create prompt)
    prompt = f"""
    You are a support agent. Answer the question based ONLY on the context below.
    
    Context:
    {context_text}
    
    Question: {question}
    """
    
    # 3. Generate
    response = llm_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    print(f"Answer: {response.choices[0].message.content}")

if __name__ == "__main__":
    ask_rag("What is the speed limit in the city?")
    ask_rag("How long should I rest after driving?")
