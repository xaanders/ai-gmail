from flask import Flask, request, jsonify, redirect, url_for
from gmail import GmailHandler
from crew import EmailCrew
import json
from summarize_mails import summarize_mails
from respond_drafts import respond_drafts

app = Flask(__name__)

@app.route('/auth/gmail/init', methods=['GET'])
def init_gmail_auth():
    """Initialize Gmail authentication"""
    try:
        # Modify GmailHandler to return the authorization URL
        gmail_handler = GmailHandler()
        
        auth_url = gmail_handler.get_authorization_url()
        return jsonify({
            'auth_url': auth_url,
            'status': 'redirect_needed'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/auth/gmail/callback')
def gmail_callback():
    """Handle Gmail OAuth callback"""
    try:
        # Get authorization code from request
        auth_code = request.args.get('code')
        if not auth_code:
            return jsonify({'error': 'No authorization code received'}), 400
        gmail_handler = GmailHandler()

        # Exchange auth code for credentials
        gmail_handler.handle_oauth_callback(auth_code)
        
        return jsonify({
            'status': 'success',
            'message': 'Gmail authentication successful'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

""" Actions """
@app.route('/emails/today', methods=['GET'])
def get_todays_emails():
    """Get today's emails"""
    try:
        gmail_handler = GmailHandler()
        gmail_handler.authenticate()
        valid = gmail_handler.check_token_status()['valid']
        if not valid:
            return jsonify({'error': 'Gmail token expired'}), 400

        emails = gmail_handler.get_todays_emails()
        return jsonify(emails)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/emails/analyze', methods=['GET'])
def analyze_emails():
    """Analyze emails using CrewAI"""
    try:
        gmail_handler = GmailHandler()
        gmail_handler.authenticate()
        analysis = summarize_mails(gmail_handler)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/emails/respond', methods=['GET'])
def respond_to_emails():
    """Respond to emails using CrewAI"""
    try:
        gmail_handler = GmailHandler()
        gmail_handler.authenticate()
        respond_drafts(gmail_handler)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({'error': str(e), "status": "failed"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)