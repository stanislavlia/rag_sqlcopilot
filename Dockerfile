FROM tiangolo/uvicorn-gunicorn:python3.10

COPY requirements.txt /requirements.txt
WORKDIR /
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY app.py copilot_api_wrapper.py load_context_to_vecdb.py postgres_executor_graph.py retrieval_graph.py sql_generator.py /
COPY chroma /chroma
COPY domain_context /domain_context
COPY sql_examples /sql_examples
COPY tables_info /tables_info

EXPOSE 8012

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8012"]
