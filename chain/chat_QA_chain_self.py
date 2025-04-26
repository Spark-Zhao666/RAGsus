from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA,ConversationalRetrievalChain
from langchain_community.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
import sys
sys.path.append("../")
from chain.model_to_llm import model_to_llm
from chain.get_vectordb import get_vectordb
import re
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import gradio as gr

class Chat_QA_chain_self:
    """"
    带历史记录的问答链  
    - model：调用的模型名称
    - temperature：温度系数，控制生成的随机性
    - top_k：返回检索的前k个相似文档
    - chat_history：历史记录，输入一个列表，默认是一个空列表
    - history_len：控制保留的最近 history_len 次对话
    - file_path：建库文件所在路径
    - persist_path：向量数据库持久化路径
    - appid：星火
    - api_key：星火、百度文心、OpenAI、智谱都需要传递的参数
    - Spark_api_secret：星火秘钥
    - Wenxin_secret_key：文心秘钥
    - embeddings：使用的embedding模型
    - embedding_key：使用的embedding模型的秘钥（智谱或者OpenAI）  
    """

    def __init__(self,model:str, temperature:float=0.0, top_k:int=4, chat_history:list=[], file_path:str=None, persist_path:str=None, appid:str=None, api_key:str=None, Spark_api_secret:str=None,Wenxin_secret_key:str=None, embedding = "openai-embedding",embedding_key:str=None, stream=False):
        self.model = model
        self.temperature = temperature
        self.top_k = top_k
        self.chat_history = chat_history
        #self.history_len = history_len
        self.file_path = file_path
        self.persist_path = persist_path
        self.appid = appid
        self.api_key = api_key
        self.Spark_api_secret = Spark_api_secret
        self.Wenxin_secret_key = Wenxin_secret_key
        self.embedding = embedding
        self.embedding_key = embedding_key
        self.default_template_rq = """
            You are a music therapist. Your task is to help the user find a song that can soothe their emotions.
            You will follow these steps:
            1. Figure out their emotions from input of the user's text.
            2. If you are not sure about the emotions, based on the knowledge you know, you can ask follow up questions to clarify.
            3. Once you are certain about the emotions, you can start to ask their favorite genres of music.
            4. Once you are certain about the music gernes, based on their emotions, generate a prompt the user can use to feed in SUNO AI to generate a song that would soothe their emotions.
            (Respond in the format: "Here is a SUNO AI prompt: <prompt>. I will play that song for you. Please rate the song on a scale of 1-5.")
            5. After the user provides the rating, you can ask them to provide feedback on the song.
            6. After the user provides the feedback, you can generate a another song (using in the format provide).
            7. Repeat steps 4-6 until the user is satisfied with the song.

            Your responces should not violate the basic protacols of psyschological therapy.
            Make sure to express the answer not in bullet points but in a complete sentence.
            Each step should be done in a separate conversation with the user.
            Keep the responce short and concise in 1 sentence only.
            {context}
            User input: {question}
            """
        self.vectordb = get_vectordb(self.file_path, self.persist_path, self.embedding,self.embedding_key)
        self.stream = stream
    def clear_history(self):
        "清空历史记录"
        return self.chat_history.clear()
    
    def change_history_length(self,history_len:int=1):
        """
        保存指定对话轮次的历史记录
        输入参数：
        - history_len ：控制保留的最近 history_len 次对话
        - chat_history：当前的历史对话记录
        输出：返回最近 history_len 次对话
        """
        n = len(self.chat_history)
        return self.chat_history[n-history_len:]
    
    def answer(self, question:str=None,temperature = None, top_k = 4, stream=False):
        """"
        核心方法，调用问答链
        arguments: 
        - question：用户提问
        """

        if len(question) == 0:
            return "", self.chat_history
        
        if temperature == None:
            temperature = self.temperature
        
        llm = model_to_llm(self.model, temperature, self.appid, self.api_key, self.Spark_api_secret, self.Wenxin_secret_key)

        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        retriever = self.vectordb.as_retriever(search_type="similarity",   
                                               search_kwargs={'k': top_k})


        qa_chain_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=self.default_template_rq
        )

        qa = ConversationalRetrievalChain.from_llm(
            llm = llm,
            retriever = retriever,
            memory = self.memory,
            combine_docs_chain_kwargs={"prompt": qa_chain_prompt}
        )

        result = qa({"question": question, 
                     "chat_history": self.chat_history})
        if stream:
            full_response = ""
            for chunk in result["answer"]:
                full_response += chunk
                yield full_response
        else:
            answer = result["answer"]
            answer = re.sub(r"\\n", '<br/>', answer)
            self.chat_history.append((question, answer))
            return self.chat_history
    
def create_gradio_interface(chat_qa_chain):
    """
    创建 Gradio 界面
    """
    with gr.Blocks(title="Chat_QA_chain_self 测试") as interface:
        gr.Markdown("# Chat_QA_chain_self 测试界面")

        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(label="对话历史")
                input_box = gr.Textbox(
                    label="输入问题",
                    placeholder="请输入您的问题...",
                    lines=5,
                    max_lines=10
                )
                with gr.Row():
                    submit_btn = gr.Button("提交", variant="primary")
                    clear_btn = gr.Button("清空")

                params = gr.Accordion("高级参数", open=False)
                with params:
                    temperature = gr.Slider(0, 1, value=0.3,
                                            label="温度系数")
                    top_k = gr.Slider(1, 10, value=4, step=1, label="Top K")
                    stream = gr.Checkbox(value=True, label="流式输出")

        # 事件处理
        def respond(message, chat_history, temp, k, stream):
            chat_history = chat_history + [[message, ""]]
            response = chat_qa_chain.answer(message, temperature=temp, top_k=k, stream=stream)
            if stream:
                previous_content = ""
                for chunk in response:
                    if chunk:  # 确保 chunk 不为空
                        current_content = chunk[len(previous_content):]
                        previous_content = chunk
                        chat_history[-1][1] += current_content  # 直接追加 chunk
                        yield "", chat_history
            else:
                # 非流式模式直接返回完整回答
                answer = next(response) if hasattr(response, "__iter__") else response
                chat_history[-1][1] = answer
                yield "", chat_history

        submit_btn.click(
            fn=respond,
            inputs=[input_box, chatbot, temperature, top_k, stream],
            outputs=[input_box, chatbot]
        )

        clear_btn.click(
            lambda: ([], []),
            outputs=[input_box, chatbot]
        )

    return interface

if __name__ == "__main__":
    # 测试 Chat_QA_chain_self 的流式回答功能
    model = "deepseek-chat"
    temperature = 0.7
    top_k = 3
    chat_history = []
    file_path = "../knowledge_db"
    persist_path = "../vector_db/chroma"
    # appid = "your_appid"
    # api_key = "sk-99e8b6b0c9d64927885f845cf447d914"
    # Spark_api_secret = "your_spark_secret"
    # Wenxin_secret_key = "your_wenxin_secret"

    # 初始化 Chat_QA_chain_self 实例
    chat_qa_chain = Chat_QA_chain_self(
        model=model,
        temperature=temperature,
        top_k=top_k,
        chat_history=chat_history,
        file_path=file_path,
        persist_path=persist_path,
        api_key=None
    )

    interface = create_gradio_interface(chat_qa_chain)
    interface.launch(share=False)
    # # 测试问题
    # question = "你能推荐一首舒缓情绪的音乐吗？"

    # # 打印最终的聊天历史记录
    # print("\n\n最终聊天历史记录：")
    # for q, a in chat_qa_chain.chat_history:
    #     print(f"问题: {q}")
    #     print(f"回答: {a}")
