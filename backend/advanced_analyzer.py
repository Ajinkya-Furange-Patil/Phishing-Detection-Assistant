"""
Advanced Phishing Email Analyzer
Provides comprehensive analysis including red flags, social engineering techniques,
and actionable recommendations.
"""

import re
from datetime import datetime
from typing import Dict, List, Any

class PhishingAnalyzer:
    """Advanced analyzer for detecting phishing characteristics and social engineering tactics."""
    
    def __init__(self):
        # Red flag patterns
        self.urgent_keywords = [
            'urgent', 'immediate', 'act now', 'limited time', 'expires today',
            'immediate action', 'respond immediately', 'time sensitive', 'hurry',
            'don\'t wait', 'act fast', 'last chance', 'final notice'
        ]
        
        self.suspicious_words = [
            'verify', 'confirm', 'update', 'suspended', 'locked', 'unusual activity',
            'click here', 'click below', 'account', 'security alert', 'validation',
            'authenticate', 'reactivate', 'reset password', 'billing problem',
            'payment failed', 'card declined'
        ]
        
        self.prize_scam_words = [
            'winner', 'won', 'prize', 'congratulations', 'claim', 'reward',
            'free', 'gift', 'selected', 'lucky', 'lottery', 'sweepstakes'
        ]
        
        self.financial_keywords = [
            'bank', 'payment', 'credit card', 'debit card', 'account number',
            'ssn', 'social security', 'routing number', 'paypal', 'wire transfer',
            'refund', 'tax', 'irs', 'invoice'
        ]
        
        self.threat_keywords = [
            'suspend', 'terminated', 'disabled', 'closed', 'blocked', 'banned',
            'delete', 'remove', 'legal action', 'court', 'lawsuit', 'penalty'
        ]
        
        # Social engineering techniques
        self.social_engineering_patterns = {
            'urgency': self.urgent_keywords,
            'fear': self.threat_keywords,
            'greed': self.prize_scam_words,
            'authority': ['ceo', 'manager', 'admin', 'support', 'security team', 'help desk'],
            'trust': ['verified', 'secure', 'protected', 'guaranteed', 'official'],
            'curiosity': ['see who', 'find out', 'discover', 'check this', 'view']
        }
    
    def analyze_email(self, 
                     email_content: str, 
                     subject: str = '', 
                     sender: str = '',
                     phishing_probability: float = 0.0) -> Dict[str, Any]:
        """
        Comprehensive email analysis.
        
        Args:
            email_content: Full email body text
            subject: Email subject line
            sender: Sender email address
            phishing_probability: ML model's phishing probability (0-1)
        
        Returns:
            Comprehensive analysis dictionary
        """
        
        text_lower = f"{subject} {email_content}".lower()
        
        red_flags = self._detect_red_flags(text_lower, sender)
        social_engineering = self._detect_social_engineering(text_lower)
        sender_analysis = self._analyze_sender(sender)
        url_analysis = self._analyze_urls(email_content)
        content_analysis = self._analyze_content(email_content, subject)
        threat_indicators = self._calculate_threat_score(text_lower, sender)
        
        # Calculate hybrid probability:
        # Heuristic base from threat score
        heuristic_prob = threat_indicators['score'] / 100.0
        
        # Combine ML probability and Heuristic score
        combined_prob = max(phishing_probability, heuristic_prob)
        
        # Check if there are specific red flags to set minimum thresholds
        has_high_red_flag = any(flag['severity'] == 'HIGH' for flag in red_flags)
        has_medium_red_flag = any(flag['severity'] == 'MEDIUM' for flag in red_flags)
        
        if has_high_red_flag:
            combined_prob = max(combined_prob, 0.70) # Ensure it's at least 70% (HIGH risk)
        elif has_medium_red_flag:
            combined_prob = max(combined_prob, 0.35) # Ensure it's at least 35% (MEDIUM risk)
            
        # Ensure sender risk or URL risk also bumps it up
        if sender_analysis.get('risk') == 'HIGH' or url_analysis.get('risk') == 'HIGH':
            combined_prob = max(combined_prob, 0.75)
        elif sender_analysis.get('risk') == 'MEDIUM' or url_analysis.get('risk') == 'MEDIUM':
            combined_prob = max(combined_prob, 0.40)
            
        analysis = {
            'phishing_probability': combined_prob,
            'risk_level': self._determine_risk_level(combined_prob),
            'red_flags': red_flags,
            'social_engineering': social_engineering,
            'sender_analysis': sender_analysis,
            'url_analysis': url_analysis,
            'content_analysis': content_analysis,
            'recommended_actions': self._generate_recommendations(combined_prob, text_lower, sender),
            'employee_awareness': self._generate_awareness_advice(text_lower),
            'threat_indicators': threat_indicators,
            'timestamp': datetime.now().isoformat()
        }
        
        return analysis
    
    def _determine_risk_level(self, probability: float) -> str:
        """Determine risk level based on probability."""
        if probability >= 0.7:
            return 'HIGH'
        elif probability >= 0.3:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _detect_red_flags(self, text: str, sender: str) -> List[Dict[str, str]]:
        """Detect red flags in email."""
        red_flags = []
        
        # Check for urgent language
        urgent_found = [word for word in self.urgent_keywords if word in text]
        if urgent_found:
            red_flags.append({
                'type': 'Urgency',
                'severity': 'HIGH',
                'description': f'Urgent language detected: {", ".join(urgent_found[:3])}',
                'indicator': 'Pressures recipient to act quickly without thinking'
            })
        
        # Check for suspicious requests
        suspicious_found = [word for word in self.suspicious_words if word in text]
        if suspicious_found:
            red_flags.append({
                'type': 'Suspicious Request',
                'severity': 'HIGH',
                'description': f'Suspicious keywords found: {", ".join(suspicious_found[:3])}',
                'indicator': 'Requests sensitive actions like verification or password reset'
            })
        
        # Check for prize/reward scams
        prize_found = [word for word in self.prize_scam_words if word in text]
        if prize_found:
            red_flags.append({
                'type': 'Prize Scam',
                'severity': 'MEDIUM',
                'description': f'Prize/reward language: {", ".join(prize_found[:3])}',
                'indicator': 'Too good to be true offers'
            })
        
        # Check for financial information requests
        financial_found = [word for word in self.financial_keywords if word in text]
        if financial_found:
            red_flags.append({
                'type': 'Financial Request',
                'severity': 'HIGH',
                'description': f'Financial keywords: {", ".join(financial_found[:3])}',
                'indicator': 'May request sensitive financial information'
            })
        
        # Check for threats
        threat_found = [word for word in self.threat_keywords if word in text]
        if threat_found:
            red_flags.append({
                'type': 'Threatening Language',
                'severity': 'HIGH',
                'description': f'Threats detected: {", ".join(threat_found[:3])}',
                'indicator': 'Uses fear to manipulate recipient'
            })
        
        # Check URLs
        urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)
        if len(urls) > 3:
            red_flags.append({
                'type': 'Multiple URLs',
                'severity': 'MEDIUM',
                'description': f'{len(urls)} URLs found in email',
                'indicator': 'Excessive links may indicate phishing attempt'
            })
        
        # Check for mismatched domains
        if sender and '@' in sender:
            sender_domain = sender.split('@')[1].lower() if '@' in sender else ''
            suspicious_domains = ['gmail', 'yahoo', 'hotmail', 'outlook'] if any(biz in text for biz in ['bank', 'paypal', 'amazon', 'microsoft']) else []
            if any(domain in sender_domain for domain in suspicious_domains):
                red_flags.append({
                    'type': 'Domain Mismatch',
                    'severity': 'HIGH',
                    'description': f'Business email from free email service: {sender_domain}',
                    'indicator': 'Legitimate businesses use official domains'
                })
        
        # Check for spelling/grammar (simple heuristic)
        if '!!!' in text or '???' in text:
            red_flags.append({
                'type': 'Poor Formatting',
                'severity': 'LOW',
                'description': 'Excessive punctuation detected',
                'indicator': 'Unprofessional formatting common in phishing'
            })
        
        return red_flags
    
    def _detect_social_engineering(self, text: str) -> Dict[str, Any]:
        """Detect social engineering techniques."""
        techniques_found = []
        
        for technique, keywords in self.social_engineering_patterns.items():
            found_keywords = [kw for kw in keywords if kw in text]
            if found_keywords:
                techniques_found.append({
                    'technique': technique.title(),
                    'description': self._get_technique_description(technique),
                    'keywords_found': found_keywords[:3],
                    'severity': self._get_technique_severity(technique),
                    'explanation': self._get_technique_explanation(technique)
                })
        
        return {
            'techniques_detected': len(techniques_found),
            'details': techniques_found,
            'overall_risk': 'HIGH' if len(techniques_found) >= 3 else 'MEDIUM' if len(techniques_found) >= 2 else 'LOW'
        }
    
    def _get_technique_description(self, technique: str) -> str:
        """Get description for social engineering technique."""
        descriptions = {
            'urgency': 'Creates false sense of urgency to bypass rational thinking',
            'fear': 'Uses threats and negative consequences to manipulate',
            'greed': 'Appeals to desire for money or prizes',
            'authority': 'Impersonates authority figures to gain compliance',
            'trust': 'Uses trust signals to appear legitimate',
            'curiosity': 'Exploits natural curiosity to get clicks'
        }
        return descriptions.get(technique, 'Unknown technique')
    
    def _get_technique_severity(self, technique: str) -> str:
        """Get severity level for technique."""
        high_severity = ['fear', 'authority', 'urgency']
        return 'HIGH' if technique in high_severity else 'MEDIUM'
    
    def _get_technique_explanation(self, technique: str) -> str:
        """Get explanation of how technique works."""
        explanations = {
            'urgency': 'Attacker wants you to act before thinking critically about the request',
            'fear': 'Designed to panic you into taking immediate action without verification',
            'greed': 'Exploits desire for free money/prizes - if it seems too good to be true, it probably is',
            'authority': 'Pretends to be someone in power to make you comply without questioning',
            'trust': 'Uses words like "secure" and "verified" to seem legitimate',
            'curiosity': 'Wants you to click links to "find out more" or "see who"'
        }
        return explanations.get(technique, '')
    
    def _analyze_sender(self, sender: str) -> Dict[str, Any]:
        """Analyze sender information."""
        if not sender or '@' not in sender:
            return {
                'valid': False,
                'risk': 'UNKNOWN',
                'issues': ['No sender information provided']
            }
        
        issues = []
        domain = sender.split('@')[1].lower() if '@' in sender else ''
        
        # Check for free email services
        free_services = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com']
        if domain in free_services:
            issues.append('Using free email service - legitimate businesses typically use official domains')
        
        # Check for suspicious patterns
        if re.search(r'\d{3,}', sender):
            issues.append('Contains many numbers - suspicious pattern')
        
        if '-' in domain or '_' in domain:
            issues.append('Domain contains hyphens/underscores - could be impersonation')
        
        if len(domain.split('.')) > 3:
            issues.append('Complex domain structure - may be spoofing')
        
        risk = 'HIGH' if len(issues) >= 2 else 'MEDIUM' if len(issues) == 1 else 'LOW'
        
        return {
            'email': sender,
            'domain': domain,
            'valid': True,
            'risk': risk,
            'issues': issues if issues else ['No obvious issues detected']
        }
    
    def _analyze_urls(self, text: str) -> Dict[str, Any]:
        """Analyze URLs in email."""
        urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)
        
        suspicious_indicators = []
        
        for url in urls:
            # Check for IP addresses
            if re.search(r'\d+\.\d+\.\d+\.\d+', url):
                suspicious_indicators.append('URL uses IP address instead of domain name')
            
            # Check for shortened URLs
            short_domains = ['bit.ly', 'tinyurl', 't.co', 'goo.gl', 'ow.ly']
            if any(short in url.lower() for short in short_domains):
                suspicious_indicators.append('Uses URL shortener - hides real destination')
            
            # Check for suspicious TLDs
            suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz']
            if any(tld in url.lower() for tld in suspicious_tlds):
                suspicious_indicators.append('Uses suspicious top-level domain')
            
            # Check for @ symbol (redirect trick)
            if '@' in url:
                suspicious_indicators.append('URL contains @ symbol - redirect trick')
        
        return {
            'total_urls': len(urls),
            'urls_found': urls[:5],  # Show first 5
            'risk': 'HIGH' if suspicious_indicators else 'MEDIUM' if len(urls) > 3 else 'LOW',
            'issues': list(set(suspicious_indicators)) if suspicious_indicators else ['No obvious URL issues']
        }
    
    def _analyze_content(self, content: str, subject: str) -> Dict[str, Any]:
        """Analyze email content characteristics."""
        return {
            'length': len(content),
            'has_html': bool(re.search(r'<[^>]+>', content)),
            'exclamation_marks': content.count('!'),
            'question_marks': content.count('?'),
            'all_caps_words': len(re.findall(r'\b[A-Z]{3,}\b', content)),
            'money_symbols': content.count('$') + content.count('€') + content.count('£'),
            'subject_length': len(subject),
            'subject_caps': subject.isupper() if subject else False
        }
    
    def _generate_recommendations(self, probability: float, text: str, sender: str) -> List[Dict[str, str]]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if probability >= 0.7:
            recommendations.append({
                'priority': 'CRITICAL',
                'action': 'Do NOT interact with this email',
                'reason': 'High probability of phishing attack',
                'steps': [
                    'Do not click any links',
                    'Do not download attachments',
                    'Do not reply to the sender',
                    'Report to IT/Security team immediately',
                    'Delete the email'
                ]
            })
        elif probability >= 0.3:
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Exercise extreme caution',
                'reason': 'Medium probability of phishing',
                'steps': [
                    'Verify sender through official channels',
                    'Do not click links - type URLs manually',
                    'Check for red flags carefully',
                    'When in doubt, report to IT',
                    'Do not provide sensitive information'
                ]
            })
        else:
            recommendations.append({
                'priority': 'LOW',
                'action': 'Appears safe, but remain vigilant',
                'reason': 'Low probability, but always verify important requests',
                'steps': [
                    'Still verify unexpected requests',
                    'Hover over links before clicking',
                    'Be cautious with attachments',
                    'Report if anything seems suspicious'
                ]
            })
        
        # Add specific recommendations based on content
        if any(word in text for word in ['password', 'verify', 'confirm']):
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Never provide credentials via email',
                'reason': 'Email requests password/verification',
                'steps': [
                    'Legitimate companies never ask for passwords via email',
                    'Go directly to official website',
                    'Use saved bookmarks, not email links',
                    'Enable two-factor authentication'
                ]
            })
        
        if re.findall(r'https?://', text):
            recommendations.append({
                'priority': 'MEDIUM',
                'action': 'Verify all links before clicking',
                'reason': 'Email contains URLs',
                'steps': [
                    'Hover over links to see real destination',
                    'Type URLs manually instead of clicking',
                    'Check for HTTPS and correct domain',
                    'Use antivirus/link checker tools'
                ]
            })
        
        return recommendations
    
    def _generate_awareness_advice(self, text: str) -> Dict[str, Any]:
        """Generate employee awareness and training advice."""
        
        # Identify what employees should learn from this example
        learning_points = []
        
        if any(word in text for word in self.urgent_keywords):
            learning_points.append({
                'topic': 'Urgency Tactics',
                'lesson': 'Phishers create false urgency to prevent careful thinking',
                'tip': 'Legitimate companies give reasonable time for important actions',
                'example': 'Real banks don\'t threaten immediate account closure'
            })
        
        if any(word in text for word in self.suspicious_words):
            learning_points.append({
                'topic': 'Verification Requests',
                'lesson': 'Be suspicious of unexpected verification/confirmation requests',
                'tip': 'Always verify through official channels, not email links',
                'example': 'If your bank emails about an issue, call the number on your card'
            })
        
        if re.search(r'https?://', text):
            learning_points.append({
                'topic': 'Link Safety',
                'lesson': 'Phishing emails often contain malicious links',
                'tip': 'Hover over links to see real destination before clicking',
                'example': 'Link text may say "paypal.com" but actually goes to "paypa1.com"'
            })
        
        if any(word in text for word in self.prize_scam_words):
            learning_points.append({
                'topic': 'Too Good to Be True',
                'lesson': 'If you didn\'t enter a contest, you didn\'t win',
                'tip': 'Free money/prizes are almost always scams',
                'example': 'Legitimate contests don\'t require payment to claim prizes'
            })
        
        return {
            'learning_points': learning_points,
            'general_advice': self._get_general_security_advice(),
            'training_recommendation': self._get_training_recommendation(len(learning_points)),
            'quiz_questions': self._generate_quiz_questions(text)
        }
    
    def _get_general_security_advice(self) -> List[str]:
        """Get general security awareness advice."""
        return [
            '🔒 Think before you click - Take time to evaluate emails carefully',
            '🔍 Verify sender identity - Contact through official channels',
            '🚫 Never share passwords via email - Legitimate companies never ask',
            '🔗 Hover over links - Check destination before clicking',
            '📞 When in doubt, call - Use official phone numbers, not from email',
            '🛡️ Enable 2FA - Add extra layer of security to accounts',
            '📧 Report suspicious emails - Help protect others',
            '🎓 Stay educated - Phishing tactics constantly evolve'
        ]
    
    def _get_training_recommendation(self, techniques_found: int) -> str:
        """Recommend training based on techniques found."""
        if techniques_found >= 3:
            return 'HIGH PRIORITY: This email demonstrates multiple sophisticated phishing techniques. Recommend comprehensive security awareness training for all employees.'
        elif techniques_found >= 2:
            return 'MEDIUM PRIORITY: Contains common phishing tactics. Regular security reminders and refresher training recommended.'
        else:
            return 'LOW PRIORITY: Basic phishing awareness training sufficient. Focus on general email security hygiene.'
    
    def _generate_quiz_questions(self, text: str) -> List[Dict[str, Any]]:
        """Generate quiz questions based on email content."""
        questions = []
        
        if any(word in text for word in self.urgent_keywords):
            questions.append({
                'question': 'What should you do when an email creates a sense of urgency?',
                'correct_answer': 'Slow down and verify the request through official channels',
                'wrong_answers': [
                    'Act quickly to avoid problems',
                    'Forward to colleagues immediately',
                    'Click the link to resolve the issue'
                ],
                'explanation': 'Urgency is a common phishing tactic to prevent careful thinking'
            })
        
        if re.search(r'https?://', text):
            questions.append({
                'question': 'Before clicking a link in an email, you should:',
                'correct_answer': 'Hover over the link to see the real destination URL',
                'wrong_answers': [
                    'Click it quickly to see where it goes',
                    'Trust it if the email looks professional',
                    'Check if the link text looks legitimate'
                ],
                'explanation': 'Link text can be misleading - always check the actual destination'
            })
        
        return questions
    
    def _calculate_threat_score(self, text: str, sender: str) -> Dict[str, Any]:
        """Calculate overall threat score."""
        score = 0
        max_score = 100
        indicators = []
        
        # Urgent language (20 points)
        if any(word in text for word in self.urgent_keywords):
            score += 20
            indicators.append('Urgent language')
        
        # Suspicious requests (20 points)
        if any(word in text for word in self.suspicious_words):
            score += 20
            indicators.append('Suspicious requests')
        
        # Multiple URLs (15 points)
        urls = len(re.findall(r'https?://', text))
        if urls > 2:
            score += 15
            indicators.append(f'{urls} URLs found')
        
        # Financial keywords (15 points)
        if any(word in text for word in self.financial_keywords):
            score += 15
            indicators.append('Financial requests')
        
        # Threats (15 points)
        if any(word in text for word in self.threat_keywords):
            score += 15
            indicators.append('Threatening language')
        
        # Prize scam (10 points)
        if any(word in text for word in self.prize_scam_words):
            score += 10
            indicators.append('Prize/reward claims')
        
        # Sender issues (5 points)
        if sender:
            domain = sender.split('@')[1] if '@' in sender else ''
            if domain in ['gmail.com', 'yahoo.com', 'hotmail.com']:
                score += 5
                indicators.append('Free email service')
        
        threat_level = 'CRITICAL' if score >= 70 else 'HIGH' if score >= 50 else 'MEDIUM' if score >= 30 else 'LOW'
        
        return {
            'score': score,
            'max_score': max_score,
            'percentage': (score / max_score) * 100,
            'threat_level': threat_level,
            'indicators': indicators
        }


def format_analysis_report(analysis: Dict[str, Any]) -> str:
    """Format analysis into a professional, formal plain-text audit report."""
    report = []
    report.append("+" + "-" * 78 + "+")
    report.append("|" + " " * 24 + "PHISHING SECURITY AUDIT REPORT" + " " * 24 + "|")
    report.append("+" + "-" * 78 + "+")
    report.append(f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Security Engine: PhishGuard AI Threat Detection v2.1")
    report.append("+" + "-" * 78 + "+")
    
    report.append("\n1. RISK ASSESSMENT")
    report.append(f"   - Phishing Probability  : {analysis['phishing_probability']*100:.2f}%")
    report.append(f"   - Risk Classification   : {analysis['risk_level']}")
    report.append(f"   - Heuristic Threat Score: {analysis['threat_indicators']['score']}/{analysis['threat_indicators']['max_score']} ({analysis['threat_indicators']['percentage']:.1f}%)")
    
    if analysis['red_flags']:
        report.append(f"\n2. DETECTED SECURITY RED FLAGS ({len(analysis['red_flags'])})")
        for i, flag in enumerate(analysis['red_flags'], 1):
            report.append(f"   [{i}] Classification: {flag['type']} (Severity: {flag['severity']})")
            report.append(f"       Description: {flag['description']}")
            report.append(f"       Threat Indicator: {flag['indicator']}")
    
    if analysis['social_engineering']['details']:
        report.append(f"\n3. SOCIAL ENGINEERING TECHNIQUES IDENTIFIED ({analysis['social_engineering']['techniques_detected']})")
        for i, tech in enumerate(analysis['social_engineering']['details'], 1):
            report.append(f"   [{i}] Technique: {tech['technique']} (Severity: {tech['severity']})")
            report.append(f"       Explanation: {tech['explanation']}")
    
    report.append(f"\n4. SENDER IDENTITY ANALYSIS")
    report.append(f"   - Sender Address: {analysis['sender_analysis'].get('email', 'N/A')}")
    report.append(f"   - Sender Risk   : {analysis['sender_analysis']['risk']}")
    if analysis['sender_analysis']['issues']:
        report.append(f"   - Identity Anomalies:")
        for issue in analysis['sender_analysis']['issues']:
            report.append(f"     * {issue}")
    
    if analysis['url_analysis']['total_urls'] > 0:
        report.append(f"\n5. EMBEDDED URL REPUTATION ANALYSIS")
        report.append(f"   - Total URLs Extracted: {analysis['url_analysis']['total_urls']}")
        report.append(f"   - Link Risk Profile   : {analysis['url_analysis']['risk']}")
        if analysis['url_analysis']['issues']:
            report.append(f"   - URL Security Issues:")
            for issue in analysis['url_analysis']['issues']:
                report.append(f"     * {issue}")
    
    report.append(f"\n6. ACTIONABLE MITIGATION STEPS")
    for i, rec in enumerate(analysis['recommended_actions'], 1):
        report.append(f"   [{i}] Priority: {rec['priority']} | Action: {rec['action']}")
        report.append(f"       Justification: {rec['reason']}")
        report.append(f"       Mitigation Procedures:")
        for step in rec['steps']:
            report.append(f"         [ ] {step}")
    
    report.append(f"\n7. CYBERSECURITY TRAINING & AWARENESS HYGIENE")
    for i, point in enumerate(analysis['employee_awareness']['learning_points'], 1):
        report.append(f"   [{i}] Educational Topic: {point['topic']}")
        report.append(f"       Key Concept      : {point['lesson']}")
        report.append(f"       Actionable Habit : {point['tip']}")
    
    report.append("\n" + "+" + "-" * 78 + "+")
    report.append("|" + " " * 20 + "END OF CYBERSECURITY ASSESSMENT REPORT" + " " * 20 + "|")
    report.append("+" + "-" * 78 + "+")
    
    return "\n".join(report)
