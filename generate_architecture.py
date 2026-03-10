
import os
import sys
from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import User
from diagrams.onprem.compute import Server
from diagrams.generic.database import SQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.network import Nginx
from diagrams.programming.framework import FastAPI, React
from diagrams.programming.language import Python
from diagrams.onprem.monitoring import Sentry
from diagrams.generic.os import Windows
from diagrams.generic.device import Tablet
from diagrams.onprem.security import Vault
from diagrams.saas.chat import Messenger

# Graphviz path setup for Windows
os.environ["PATH"] += os.pathsep + r'C:\Program Files\Graphviz\bin'

graph_attr = {
    "fontsize": "32",
    "bgcolor": "white",
    "fontname": "Verdana Bold",
    "pad": "2.0",
    "nodesep": "1.5",
    "ranksep": "2.0",
    "dpi": "300",
    "splines": "curved",
    "concentrate": "true"
}

def generate():
    with Diagram("Formazione Coemi - Architecture Blueprint", 
                 show=False, 
                 filename="docs/assets/architecture", 
                 outformat="png", 
                 graph_attr=graph_attr):
        
        user = User("End User")

        with Cluster("Client Layer (Desktop Application)"):
            with Cluster("PyQt6 GUI Framework"):
                gui = Windows("Intelleo Desktop App")
                toast = Messenger("Toast Notifications")
                voice = Tablet("Voice Assistant (pyttsx3)")
            
            api_client = Python("API Client (httpx/requests)")
            lic_mgr = Vault("License Manager")

        with Cluster("API Layer (Backend Core)"):
            app_server = FastAPI("FastAPI Server")
            sentry = Sentry("Error Tracking")
            
            with Cluster("Business Logic Services"):
                ai_service = Python("AI Extraction Service")
                sync_service = Python("Sync & Notification Service")
                scheduler = Redis("APScheduler (Tasks)")

        with Cluster("Intelligence & External"):
            gemini = Messenger("Google Gemini AI")
            external_api = Server("External Services (SMTP/GitHub)")

        with Cluster("Persistence & Security"):
            db = SQL("Local SQLite (SQLAlchemy)")
            mem_db = Redis("Memory DB Shield")
            obfuscator = Vault("String Obfuscator")

        # --- Connections ---
        
        # User Interaction
        user >> Edge(label="Interacts", color="blue", style="bold") >> gui
        
        # Internal Client Flow
        gui >> Edge(color="cyan") >> api_client
        gui >> Edge(color="purple", style="dashed") >> toast
        gui >> Edge(color="purple", style="dashed") >> voice
        api_client >> Edge(label="Auth & Config", color="orange") >> lic_mgr
        
        # API Communication
        api_client >> Edge(label="JSON/REST", color="blue", style="bold") >> app_server
        app_server >> Edge(color="red", style="dashed") >> sentry
        
        # Backend Processing
        app_server >> ai_service
        app_server >> sync_service
        sync_service >> Edge(color="darkgreen") >> scheduler
        
        # External Integrations
        ai_service >> Edge(label="Prompt Analysis", color="darkviolet") >> gemini
        sync_service >> Edge(label="Alerts/Updates", color="red") >> external_api
        
        # Storage & Security
        app_server >> Edge(label="CRUD Operations", color="orange") >> db
        db >> Edge(label="Protection Layer", color="black", style="dotted") >> mem_db
        app_server >> Edge(label="De-obfuscation", color="grey") >> obfuscator

if __name__ == "__main__":
    # Ensure assets directory exists
    os.makedirs("docs/assets", exist_ok=True)
    try:
        generate()
        print("Architecture diagram generated successfully in docs/assets/architecture.png")
    except Exception as e:
        print(f"Error generating diagram: {e}")
        print("Note: Ensure 'diagrams' and 'graphviz' are installed.")
