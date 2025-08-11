from playwright.sync_api import sync_playwright
import time
import os
import requests

def send_telegram_message(message):
    """Send a message to Telegram channel"""
    try:
        tg_token = "8240983276:AAEcLKYmOqZV9QPhwf7761CEmuICi23NHC4"
        tg_chat_id = "-1002075453681"
            
        url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
        
        response = requests.post(url, json={
            'chat_id': tg_chat_id,
            'text': message,
            'parse_mode': 'HTML'
        })
        
        if response.status_code == 200:
            print(f"[TELEGRAM] Message sent: {message}")
            return True
        else:
            print(f"[TELEGRAM] Failed to send message. Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[TELEGRAM] Error sending message: {str(e)}")
        return False

def monitor_class_content():
    # Dashboard URL to start from
    dashboard_url = "https://gordoncollegeccs.edu.ph/ccs/students/lamp/#/main/classes"
    
    # Class codes to monitor
    target_class_codes = ["40923", "40922", "40928", "40924", "40925", "40926", "40927"]
    
    # Storage for previous content
    previous_content = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Set to True for production
        page = browser.new_page()
        
        try:
            # Login process
            print("Navigating to login page...")
            page.goto("https://gordoncollegeccs.edu.ph/ccs/students/lamp/#/login")
            page.wait_for_load_state("networkidle")
            
            print("Filling login credentials...")
            page.wait_for_selector("input#param1", state="visible", timeout=10000)
            page.wait_for_selector("input#param2", state="visible", timeout=10000)
            
            page.fill("input#param1", "ur shit here")
            page.fill("input#param2", "ur shit here")
            
            print("Credentials filled. Looking for login button...")
            
            print("Attempting to click login button...")
            
            try:
                # Fuckton of fallback since gclamp uses dumb angular components that are not easy to target
                page.wait_for_selector("button.submitbutton:has-text('LOGIN')", state="visible", timeout=5000)
                page.click("button.submitbutton:has-text('LOGIN')")
                print("Successfully clicked LOGIN button")
                
                print("Waiting for login to complete...")
                page.wait_for_load_state("networkidle", timeout=15000)
                
                time.sleep(5)
                
                current_url = page.url
                print(f"Current URL after login: {current_url}")
                
                if "main" in current_url or "classes" in current_url:
                    print("Login successful! Redirected to main dashboard")
                elif "login" in current_url:
                    print("Still on login page - checking for errors...")
                    
                    error_elements = page.query_selector_all(".text-danger")
                    for error in error_elements:
                        error_text = error.text_content().strip()
                        if error_text:
                            print(f"Error message: {error_text}")
                    
                    # weird case where the login is successful but the url is not updated
                    try:
                        time.sleep(3)
                        page.wait_for_load_state("networkidle")
                        current_url = page.url
                        if "main" in current_url or "classes" in current_url:
                            print("Login actually successful - URL updated after delay")
                        else:
                            print("Login may have failed - please check manually")
                            input("Press Enter to continue anyway...")
                    except:
                        input("Press Enter to continue anyway...")
                else:
                    print("Login status unclear - proceeding with monitoring")
                    
            except Exception as e:
                print(f"Failed to click login button: {e}")
                
                try:
                    print("Trying alternative selector...")
                    visible_buttons = page.query_selector_all("button.submitbutton")
                    for i, btn in enumerate(visible_buttons):
                        if btn.is_visible() and "LOGIN" in btn.text_content():
                            btn.click()
                            print(f"Successfully clicked visible LOGIN button (index {i})")
                            page.wait_for_load_state("networkidle", timeout=15000)
                            time.sleep(5)
                            
                            current_url = page.url
                            if "main" in current_url or "classes" in current_url:
                                print("Alternative login method successful!")
                            break
                    else:
                        raise Exception("No visible LOGIN button found")
                        
                except Exception as e2:
                    print(f"Alternative method also failed: {e2}")
                    
                    page.screenshot(path="login_debug.png")
                    print("Screenshot saved as login_debug.png")
                    
                    input("Press Enter to continue after manual login...")
            
            print("Login completed! Starting to monitor class pages...\n")

            # Main loop for monitoring class content
            while True:
                # Iterate through each class code
                for i, class_code in enumerate(target_class_codes, 1):
                    print(f"Checking class {i}/{len(target_class_codes)}: {class_code}")
                    
                    # Try to find the class card with the target class code
                    try:
                        print(f"  Navigating to dashboard...")
                        page.goto(dashboard_url)
                        page.wait_for_load_state("networkidle")
                        time.sleep(2)
                        
                        print(f"  Looking for class card with code: {class_code}")
                        class_cards = page.query_selector_all(".class__card")
                        
                        class_found = False
                        # Iterate through each class card
                        for card in class_cards:
                            code_element = card.query_selector("small")
                            if code_element and class_code in code_element.text_content():
                                print(f"  Found class card for {class_code}")
                                
                                # Find the Enter button
                                enter_button = card.query_selector("button.class__enter")
                                if enter_button:
                                    print(f"  Clicking Enter button...")
                                    enter_button.click()
                                    page.wait_for_load_state("networkidle")
                                    time.sleep(3)
                                    
                                    print(f"  Extracting content...")
                                    content_elements = page.query_selector_all(".content__text")
                                    
                                    # Extract content from the class page
                                    current_content = []
                                    for element in content_elements:
                                        text = element.text_content().strip()
                                        if text:
                                            current_content.append(text)
                                    
                                    # First time visiting this class
                                    if class_code not in previous_content:
                                        previous_content[class_code] = set(current_content)
                                        print(f"  Initial content found: {len(current_content)} items")
                                        print(f"  Content: {current_content}")
                                        
                                        if current_content:
                                            print("  Content:")
                                            for content in current_content:
                                                print(f"    - {content}")
                                    else:
                                        previous_set = previous_content[class_code]
                                        current_set = set(current_content)
                                        
                                        new_content = current_set - previous_set
                                        
                                        if new_content:
                                         print(f"  NEW CONTENT DETECTED!")
                                         print(f"  New items ({len(new_content)}):")
                                         
                                         class_name = "Unknown Class"
                                         try:
                                             class_desc = card.query_selector(".class__desc")
                                             if class_desc:
                                                 class_name = class_desc.text_content().strip()
                                         except:
                                             pass
                                         
                                         telegram_message = f"<b>NEW CONTENT DETECTED!</b>\n\n"
                                         telegram_message += f"<b>Class:</b> {class_name} ({class_code})\n"
                                         telegram_message += f"<b>New Items ({len(new_content)}):</b>\n\n"
                                         
                                         for content in new_content:
                                             print(f"    + {content}")
                                             content_preview = content[:200] + "..." if len(content) > 200 else content
                                             telegram_message += f"• {content_preview}\n"
                                         
                                         send_telegram_message(telegram_message)
                                         
                                         previous_content[class_code] = current_set
                                        else:
                                            print(f"  No new content. Total items: {len(current_content)}")
                                    
                                    class_found = True
                                    break
                                else:
                                    print(f"  Enter button not found for class {class_code}")
                        
                        if not class_found:
                            print(f"  Class card for {class_code} not found on dashboard")
                        
                        print()
                        
                    except Exception as e:
                        print(f"  Error checking class {class_code}: {str(e)}")
                        continue
                
                print("Monitoring cycle complete! Waiting 30 seconds before next check...")
                time.sleep(600)
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        
        finally:
            browser.close()

if __name__ == "__main__":
    monitor_class_content()