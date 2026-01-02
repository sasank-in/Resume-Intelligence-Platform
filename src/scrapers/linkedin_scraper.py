import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class LinkedInScraper:
    def __init__(self, headless=True):
        """Initialize LinkedIn scraper with Chrome driver"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def extract_profile(self, profile_url):
        """Extract LinkedIn profile data"""
        try:
            print(f"[INFO] Scraping LinkedIn profile: {profile_url}")
            self.driver.get(profile_url)
            
            # Wait for key elements to load
            time.sleep(5)
            
            # Scroll to load lazy-loaded content
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            for i in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            profile_data = {
                "name": self._extract_name(),
                "headline": self._extract_headline(),
                "location": self._extract_location(),
                "about": self._extract_about(),
                "experience": self._extract_experience(),
                "education": self._extract_education(),
                "skills": self._extract_skills(),
                "certifications": self._extract_certifications()
            }
            
            print("[SUCCESS] LinkedIn profile extracted successfully")
            return profile_data
        
        except Exception as e:
            print(f"[WARNING] Error scraping LinkedIn: {str(e)}")
            return {
                "name": None,
                "headline": None,
                "location": None,
                "about": None,
                "experience": [],
                "education": [],
                "skills": [],
                "certifications": []
            }
        
        finally:
            self.driver.quit()
    
    def _extract_name(self):
        """Extract profile name - multiple selector options"""
        selectors = [
            ("[data-test-id='identity-headline']", By.CSS_SELECTOR),
            ("h1[class*='text-heading']", By.CSS_SELECTOR),
            ("h1", By.TAG_NAME),
            (".pv-text-details__left-panel h1", By.CSS_SELECTOR),
            ("span[class*='profile-full-name']", By.CSS_SELECTOR),
        ]
        
        for selector, by in selectors:
            try:
                elements = self.driver.find_elements(by, selector)
                for elem in elements:
                    text = elem.text.strip()
                    # Filter out empty text and common non-name elements
                    if text and len(text) > 2 and len(text) < 100 and "+" not in text:
                        return text
            except:
                pass
        
        # Last resort: try to get name from page title
        try:
            title = self.driver.title
            if " | LinkedIn" in title:
                name = title.split(" | LinkedIn")[0].strip()
                if name and len(name) > 2:
                    return name
        except:
            pass
        
        return None
    
    def _extract_headline(self):
        """Extract professional headline - multiple selector options"""
        selectors = [
            ("div.text-body-medium", By.CSS_SELECTOR),
            ("[data-test-id*='headline']", By.CSS_SELECTOR),
            ("div[class*='headline']", By.CSS_SELECTOR),
        ]
        
        for selector, by in selectors:
            try:
                elements = self.driver.find_elements(by, selector)
                for elem in elements:
                    text = elem.text.strip()
                    if text and 10 < len(text) < 200:
                        return text
            except:
                pass
        return None
    
    def _extract_location(self):
        """Extract location - multiple selector options"""
        selectors = [
            ("span.text-body-small", By.CSS_SELECTOR),
            ("[data-test-id*='location']", By.CSS_SELECTOR),
            ("span[class*='location']", By.CSS_SELECTOR),
        ]
        
        for selector, by in selectors:
            try:
                elements = self.driver.find_elements(by, selector)
                for elem in elements:
                    text = elem.text.strip()
                    if text and len(text) < 100:
                        return text
            except:
                pass
        return None
    
    def _extract_about(self):
        """Extract about section - multiple selector options"""
        selectors = [
            ("section[data-section-id='about']", By.CSS_SELECTOR),
            ("#about", By.ID),
            ("div[data-test-id='about']", By.CSS_SELECTOR),
        ]
        
        for selector, by in selectors:
            try:
                section = self.driver.find_element(by, selector)
                # Find the text content in the section
                paragraphs = section.find_elements(By.TAG_NAME, "p")
                if paragraphs:
                    text = " ".join([p.text.strip() for p in paragraphs if p.text.strip()])
                    if text:
                        return text
                # Fallback to all text in section
                text = section.text.strip()
                if text and len(text) > 20:
                    return text
            except:
                pass
        return None
    
    def _extract_experience(self):
        """Extract work experience - multiple selector options"""
        experiences = []
        try:
            # Try different experience section selectors
            exp_sections = self.driver.find_elements(By.CSS_SELECTOR, "section[data-section-id='experience']")
            if not exp_sections:
                exp_sections = self.driver.find_elements(By.ID, "experience")
            if not exp_sections:
                exp_sections = self.driver.find_elements(By.CSS_SELECTOR, "section[aria-label*='Experience']")
            
            if exp_sections:
                exp_section = exp_sections[0]
                
                # Try different item selectors
                exp_items = exp_section.find_elements(By.CSS_SELECTOR, "div[data-test-id*='experience']")
                if not exp_items:
                    exp_items = exp_section.find_elements(By.CSS_SELECTOR, "li[data-test-id*='experience']")
                if not exp_items:
                    exp_items = exp_section.find_elements(By.TAG_NAME, "li")
                
                for item in exp_items[:5]:
                    try:
                        text = item.text.strip()
                        if text and len(text) > 10:
                            lines = [l.strip() for l in text.split('\n') if l.strip()]
                            
                            if len(lines) >= 1:
                                title = lines[0]
                                company = lines[1] if len(lines) > 1 else "N/A"
                                duration = lines[2] if len(lines) > 2 else "N/A"
                                
                                # Filter out invalid entries
                                if title and title != "N/A" and len(title) < 100:
                                    experiences.append({
                                        "title": title,
                                        "company": company,
                                        "duration": duration
                                    })
                    except:
                        pass
        except:
            pass
        
        return experiences if experiences else []
    
    def _extract_education(self):
        """Extract education"""
        education = []
        try:
            edu_sections = self.driver.find_elements(By.CSS_SELECTOR, "section[data-section-id='education']")
            if not edu_sections:
                edu_sections = self.driver.find_elements(By.ID, "education")
            if not edu_sections:
                edu_sections = self.driver.find_elements(By.CSS_SELECTOR, "section[aria-label*='Education']")
            
            if edu_sections:
                edu_section = edu_sections[0]
                
                # Try different item selectors
                edu_items = edu_section.find_elements(By.CSS_SELECTOR, "div[data-test-id*='education']")
                if not edu_items:
                    edu_items = edu_section.find_elements(By.CSS_SELECTOR, "li[data-test-id*='education']")
                if not edu_items:
                    edu_items = edu_section.find_elements(By.TAG_NAME, "li")
                
                for item in edu_items[:5]:
                    try:
                        text = item.text.strip()
                        if text and len(text) > 10:
                            lines = [l.strip() for l in text.split('\n') if l.strip()]
                            
                            if len(lines) >= 1:
                                degree = lines[0]
                                institution = lines[1] if len(lines) > 1 else "N/A"
                                year = lines[2] if len(lines) > 2 else "N/A"
                                
                                if degree and degree != "N/A" and len(degree) < 100:
                                    education.append({
                                        "degree": degree,
                                        "institution": institution,
                                        "year": year
                                    })
                    except:
                        pass
        except:
            pass
        
        return education if education else []
    
    def _extract_skills(self):
        """Extract skills"""
        skills = []
        try:
            skills_sections = self.driver.find_elements(By.CSS_SELECTOR, "section[data-section-id='skills']")
            if not skills_sections:
                skills_sections = self.driver.find_elements(By.ID, "skills")
            if not skills_sections:
                skills_sections = self.driver.find_elements(By.CSS_SELECTOR, "section[aria-label*='Skills']")
            
            if skills_sections:
                skills_section = skills_sections[0]
                
                # Try different skill item selectors
                skill_items = skills_section.find_elements(By.CSS_SELECTOR, "li[data-test-id*='skill']")
                if not skill_items:
                    skill_items = skills_section.find_elements(By.TAG_NAME, "li")
                if not skill_items:
                    skill_items = skills_section.find_elements(By.CSS_SELECTOR, "button[class*='skill']")
                
                for item in skill_items[:15]:
                    try:
                        text = item.text.strip()
                        # Filter out empty, short, or common UI text
                        if text and 2 < len(text) < 50 and text not in ["Endorsements", "See more"]:
                            skills.append(text)
                    except:
                        pass
        except:
            pass
        
        return list(set(skills)) if skills else []  # Remove duplicates
    
    def _extract_certifications(self):
        """Extract certifications"""
        certifications = []
        try:
            cert_sections = self.driver.find_elements(By.CSS_SELECTOR, "section[data-section-id='certifications']")
            if not cert_sections:
                cert_sections = self.driver.find_elements(By.CSS_SELECTOR, "section[data-test-id*='certification']")
            if not cert_sections:
                cert_sections = self.driver.find_elements(By.CSS_SELECTOR, "section[aria-label*='License']")
            
            if cert_sections:
                cert_section = cert_sections[0]
                
                cert_items = cert_section.find_elements(By.CSS_SELECTOR, "li[data-test-id*='certification']")
                if not cert_items:
                    cert_items = cert_section.find_elements(By.TAG_NAME, "li")
                
                for item in cert_items[:10]:
                    try:
                        text = item.text.strip()
                        if text and len(text) > 5 and len(text) < 200:
                            certifications.append(text)
                    except:
                        pass
        except:
            pass
        
        return certifications if certifications else []
