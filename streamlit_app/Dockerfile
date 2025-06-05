# Dockerfile (streamlit_app)
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY streamlit_app/ streamlit_app/
COPY audio_outputs/ audio_outputs/
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app/app.py", "--server.port", "8501", "--server.enableCORS", "false"] 