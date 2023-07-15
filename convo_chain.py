import os
import sys
from authentication import authenticate
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from video_stats import VideoAnalytics

class ConversationChain:
    def __init__(self, video_id):
        self.credentials = authenticate()
        self.video_analytics = VideoAnalytics(self.credentials)
        self.comments = self.video_analytics.get_video_comments(video_id)
        self.extracted_comments = []

        for comment, sentiment in self.comments:
            self.extracted_comments.append(comment)

        self.text_splitter = CharacterTextSplitter(separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        self.extracted_comments_string = " ".join(self.extracted_comments)
        self.text_chunks = self.text_splitter.split_text(self.extracted_comments_string)
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = FAISS.from_texts(texts=self.text_chunks, embedding=self.embeddings)
        self.conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(
                api_key=os.getenv('OPENAI_API_KEY'),
                model_name="gpt-3.5-turbo",
                temperature=0
            ),
            retriever=self.vectorstore.as_retriever()
        )

        self.chat_history = []

    def run(self):
        while True:
            query = input(f"Prompt: ")
            if query == "exit" or query == "quit" or query == "q" or query == "f":
                sys.exit()
            if query == '':
                continue
            result = self.conversation_chain({"question": query, "chat_history": self.chat_history})
            print(f"Answer: " + result["answer"])
            self.chat_history.append((query, result["answer"]))


video_id = 'cDedvKJJ6Xg'
conversation_chain = ConversationChain(video_id)
conversation_chain.run()
