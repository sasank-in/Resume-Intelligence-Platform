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
            print(f"🔍 Scraping LinkedIn profile: {profile_url}")
            self.driver.get(profile_url)
            time.sleep(3)  # Wait for page load
            
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
            
            print("✓ LinkedIn profile extracted successfully")
            return profile_data
        
        except Exception as e:
            print(f"❌ Error scraping LinkedIn: {str(e)}")
            return None
        
        finally:
            self.driver.quit()
    
    def _extract_name(self):
        """Extract profile name"""
        try:
            name = self.driver.find_element(By.CSS_SELECTOR, "h1.text-heading-xlarge").text
            return name.strip()
        except:
            return "N/A"
    
    def _extract_headline(self):
        """Extract professional headline"""
        try:
            headline = self.driver.find_element(By.CSS_SELECTOR, "div.text-body-medium").text
            return headline.strip()
        except:
            return "N/A"
    
    def _extract_location(self):
        """Extract location"""
        try:
            location = self.driver.find_element(By.CSS_SELECTOR, "span.text-body-small").text
            return location.strip()
        except:
            return "N/A"
    
    def _extract_about(self):
        """Extract about section"""
        try:
            about_section = self.driver.find_element(By.ID, "about")
            about_text = about_section.find_element(By.CSS_SELECTOR, "div.display-flex.ph5.pv3").text
            return about_text.strip()
        except:
            return "N/A"
    
    def _extract_experience(self):
        """Extract work experience"""
        experiences = []
        try:
            exp_section = self.driver.find_element(By.ID, "experience")
            exp_items = exp_section.find_elements(By.CSS_SELECTOR, "li.artdeco-list__item")
            
            for item in exp_items[:5]:  # Limit to 5 most recent
                try:
                    title = item.find_element(By.CSS_SELECTOR, "div.display-flex.flex-column.full-width span[aria-hidden='true']").text
                    company = item.find_elements(By.CSS_SELECTOR, "span.t-14.t-normal span[aria-hidden='true']")[0].text
                    duration = item.find_elements(By.CSS_SELECTOR, "span.t-14.t-normal span[aria-hidden='true']")[1].text
                    
                    experiences.append({
                        "title": title.strip(),
                        "company": company.strip(),
                        "duration": duration.strip()
                    })
                except:
                    continue
        except:
            pass
        
        return experiences
    
    def _extract_education(self):
        """Extract education"""
        education = []
        try:
            edu_section = self.driver.find_element(By.ID, "education")
            edu_items = edu_section.find_elements(By.CSS_SELECTOR, "li.artdeco-list__item")
            
            for item in edu_items[:3]:
                try:
                    school = item.find_element(By.CSS_SELECTOR, "div.display-flex.flex-column.full-width span[aria-hidden='true']").text
                    degree = item.find_elements(By.CSS_SELECTOR, "span.t-14.t-normal span[aria-hidden='true']")[0].text
                    
                    education.append({
                        "institution": school.strip(),
                        "degree": degree.strip()
                    })
                except:
                    continue
        except:
            pass
        
        return education
    
    def _extract_skills(self):
        """Extract skills"""
        skills = []
        try:
            skills_section = self.driver.find_element(By.ID, "skills")
            skill_items = skills_section.find_elements(By.CSS_SELECTOR, "div.display-flex.align-items-center span[aria-hidden='true']")
            
            for skill in skill_items[:20]:  # Limit to 20 skills
                skill_text = skill.text.strip()
                if skill_text and len(skill_text) > 2:
                    skills.append(skill_text)
        except:
            pass
        
        return skills
    
    def _extract_certifications(self):
        """Extract certifications"""
        certifications = []
        try:
            cert_section = self.driver.find_element(By.CSS_SELECTOR, "section[data-section='certifications']")
            cert_items = cert_section.find_elements(By.CSS_SELECTOR, "li.artdeco-list__item")
            
            for cert in cert_items[:5]:
                try:
                    cert_name = cert.find_element(By.CSS_SELECTOR, "div.display-flex.flex-column.full-width span[aria-hidden='true']").text
                    certifications.append(cert_name.strip())
                except:
                    continue
        except:
            pass
        
        return certifications
