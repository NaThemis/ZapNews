#!/usr/bin/env python3
"""
Workflow Actualités Automatique - Version MVP
Coût: ~15€/mois - Développement: 1 weekend
"""

import feedparser
import openai
import smtplib
import schedule
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os

class NewsWorkflowMVP:
    def __init__(self):
        # Configuration - À adapter
        self.openai_api_key = "your-openai-key"
        self.email_from = "your-email@gmail.com"
        self.email_password = "your-app-password"  # Gmail App Password
        self.email_to = "your-email@gmail.com"
        
        # Sources RSS par catégorie
        self.rss_sources = {
            "actualite": [
                "https://www.lemonde.fr/rss/une.xml",
                "https://www.lesechos.fr/rss.xml",
                "https://feeds.feedburner.com/franceinfo-titres"
            ],
            "business": [
                "https://www.boursorama.com/rss/actualites/",
                "https://coindesk.com/arc/outboundfeeds/rss/",
                "https://feeds.bloomberg.com/markets/news.rss"
            ],
            "legal": [
                "https://www.nextinpact.com/rss/news.xml",
                "https://iapp.org/news/rss/",
                "https://www.dalloz-actualite.fr/rss.xml"
            ],
            "tech": [
                "https://techcrunch.com/feed/",
                "https://www.zdnet.fr/feeds/rss/actualites/",
                "https://news.microsoft.com/feed/"
            ]
        }
        
        openai.api_key = self.openai_api_key

    def collect_rss_news(self, category, max_articles=5):
        """Collecte les news RSS pour une catégorie"""
        articles = []
        yesterday = datetime.now() - timedelta(days=1)
        
        for rss_url in self.rss_sources.get(category, []):
            try:
                feed = feedparser.parse(rss_url)
                for entry in feed.entries[:max_articles]:
                    # Filtre articles récents (24h)
                    try:
                        pub_date = datetime(*entry.published_parsed[:6])
                        if pub_date > yesterday:
                            articles.append({
                                'title': entry.title,
                                'summary': entry.get('summary', '')[:300],
                                'link': entry.link,
                                'source': feed.feed.title
                            })
                    except:
                        # Si pas de date, on prend quand même les premiers
                        articles.append({
                            'title': entry.title,
                            'summary': entry.get('summary', '')[:300],
                            'link': entry.link,
                            'source': feed.feed.title
                        })
            except Exception as e:
                print(f"Erreur RSS {rss_url}: {e}")
        
        return articles[:max_articles]  # Limite pour économiser tokens

    def generate_section(self, category, articles):
        """Génère une section avec OpenAI"""
        
        prompts = {
            "actualite": """Tu es journaliste expert. Synthétise ces actualités françaises/internationales en format conversationnel pour discussion café/collègues:
            - 3 points marquants avec anecdotes
            - 1 chiffre/stat à retenir
            - 2 questions/réponses pour mémoriser
            - 1 idée d'article blog (angle cybersécurité/IA/droit)
            - 1 ressource pour approfondir""",
            
            "business": """Tu es analyste financier. Synthétise ces infos business/investissement:
            - Impact sur marchés tech/crypto/actions EU
            - 1 opportunité d'investissement concrète avec justification
            - Insights économiques pour briller en réunion
            - 2 Q/R sur l'économie
            - 1 idée article blog (fintech/IA/data protection)
            - 1 ressource approfondie""",
            
            "legal": """Tu es juriste spécialisé tech. Synthétise ces actualités légales:
            - Évolutions RGPD/IA Act/IP
            - Impact pratique sur entreprises tech
            - Point de vigilance juridique
            - 2 Q/R juridique-tech
            - 1 idée article (guide juridique tech/IA/data)
            - 1 ressource juridique""",
            
            "tech": """Tu es expert tech. Synthétise en 4 sous-parties:
            A) IA: nouveaux modèles, impacts business
            B) Data Engineering: plateformes (Databricks/Azure/AWS), catalogues
            C) Cybersécurité: attaques récentes, recommandations
            D) GAFAM/Microsoft: annonces majeures
            + 2 Q/R techniques + 1 idée article + 1 ressource"""
        }
        
        articles_text = "\n".join([f"- {art['title']}: {art['summary']}" for art in articles])
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Plus économique que GPT-4
                messages=[
                    {"role": "system", "content": prompts[category]},
                    {"role": "user", "content": f"Articles du jour:\n{articles_text}"}
                ],
                max_tokens=800,  # Limite pour économiser
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Erreur génération {category}: {e}"

    def generate_daily_email(self):
        """Génère l'email quotidien complet"""
        
        print("🔄 Collecte des actualités...")
        
        # Collecte par catégorie
        news_data = {}
        for category in self.rss_sources.keys():
            print(f"📰 Collecte {category}...")
            news_data[category] = self.collect_rss_news(category)
        
        print("🤖 Génération IA des synthèses...")
        
        # Génération des sections
        sections = {}
        section_titles = {
            "actualite": "📰 ACTUALITÉ GÉNÉRALE",
            "business": "💼 BUSINESS & INVESTISSEMENT", 
            "legal": "⚖️ ACTUALITÉS LÉGALES",
            "tech": "🚀 ACTUALITÉS TECHNO"
        }
        
        for category, articles in news_data.items():
            if articles:  # Seulement si on a des articles
                print(f"✍️ Génération section {category}...")
                sections[category] = self.generate_section(category, articles)
        
        # Template email final
        email_content = f"""
<html><body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">

<h1 style="color: #2c3e50; border-bottom: 3px solid #3498db;">🌅 Votre Synthèse Quotidienne - {datetime.now().strftime('%d/%m/%Y')}</h1>

{chr(10).join([f'<div style="margin: 30px 0; padding: 20px; border-left: 4px solid #3498db; background-color: #f8f9fa;"><h2 style="color: #2c3e50;">{section_titles[cat]}</h2><div style="white-space: pre-line;">{content}</div></div>' for cat, content in sections.items()])}

<div style="margin: 40px 0; padding: 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; text-align: center;">
<h2 style="color: white; margin-bottom: 15px;">🌟 INSPIRATION DU JOUR</h2>
<p style="font-size: 16px; font-style: italic; margin: 0;">
"L'innovation naît de l'audace de transformer l'incertitude en opportunité. 
Chaque erreur est un pas vers la maîtrise, chaque échec une leçon vers l'excellence. 
Osez, expérimentez, échouez brillamment - car c'est dans l'exploration des limites que se révèlent les véritables percées."
</p>
</div>

<footer style="margin-top: 40px; padding: 20px; background-color: #f1f2f6; text-align: center; border-radius: 5px;">
<p style="color: #666; margin: 0;">📧 Synthèse générée automatiquement par votre assistant IA personnel</p>
<p style="color: #666; margin: 5px 0 0 0; font-size: 12px;">Développé avec ❤️ en Python + OpenAI</p>
</footer>

</body></html>
        """
        
        return email_content

    def send_email(self, content):
        """Envoie l'email via Gmail SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🌅 Synthèse Quotidienne - {datetime.now().strftime('%d/%m')}"
            msg['From'] = self.email_from
            msg['To'] = self.email_to
            
            html_part = MIMEText(content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Connexion Gmail SMTP
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email_from, self.email_password)
            server.send_message(msg)
            server.quit()
            
            print("✅ Email envoyé avec succès!")
            
        except Exception as e:
            print(f"❌ Erreur envoi email: {e}")

    def run_daily_workflow(self):
        """Lance le workflow quotidien"""
        print(f"🚀 Début workflow - {datetime.now()}")
        
        try:
            email_content = self.generate_daily_email()
            self.send_email(email_content)
            print("✅ Workflow terminé avec succès!")
            
        except Exception as e:
            print(f"❌ Erreur workflow: {e}")

# Configuration et lancement
def main():
    workflow = NewsWorkflowMVP()
    
    # Test immédiat (optionnel)
    # workflow.run_daily_workflow()
    
    # Programmation quotidienne à 7h30
    schedule.every().day.at("07:30").do(workflow.run_daily_workflow)
    
    print("⏰ Workflow programmé pour 7h30 chaque jour")
    print("🔄 En attente... (Ctrl+C pour arrêter)")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Vérif chaque minute

if __name__ == "__main__":
    main()