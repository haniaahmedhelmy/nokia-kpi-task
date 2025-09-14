# nokia-kpi-task
This application is a full-stack system built to generate Excel reports, export them to PowerPoint, and send them automatically via email scheduling. It integrates FastAPI (backend) with React + Material-UI (frontend), and supports user authentication, scheduling, and automated email reporting.

How to Run the Application
Backend (FastAPI)
Navigate to the backend/ folder and run:
uvicorn app:app --reload
Runs the backend at http://localhost:8000
Swagger docs: http://localhost:8000/docs

Frontend (React)
Navigate to the frontend/settings-ui folder and run:
npm install   # first time only
npm run dev
Runs the frontend at http://localhost:5173


backend . env 
DATASET_PATH=./dataset.csv
OUTPUT_DIR=./out
# Gmail SMTP settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=haniahelmy20@gmail.com
SMTP_PASS=xzpkklfcdssdxdqk  
SMTP_FROM=haniahelmy20@gmail.com
# Database + App
DATABASE_URL=postgresql://neondb_owner:npg_Kl2hV6dDzCou@ep-orange-shape-adp1vijl-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
SECRET_KEY=a4f8e2d9c76b4f7b83df45f9ad8e33a2e2c0d423f45e1c99f33bbfc01a9f11cd
CORS_ORIGIN=http://localhost:5173
TOKEN_MINUTES=1440


Frontend .en
VITE_API_URL=http://localhost:8000


install dependecy 
pip install -r requirements.txt

