import os
import sys
import time
import warnings
from random import uniform
from getpass import getpass

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seletools.actions import drag_and_drop

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)


class zyBooks(object):
    def __init__(self):
        self.fetch_info()
        self.driver = webdriver.Edge(options=self.options)

    def fetch_info(self):
        print("Fetching Info . . .")
        self.options = Options()
        self.options.add_argument("log-level=3")
        self.options.add_experimental_option("excludeSwitches",
                                             ["enable-logging"])
        self.options.headless = True
        self.email = "" or input("Enter Email: ")
        self.password = "" or getpass("Enter Password: ")
        self.course = "" or input("Enter Course: ")
        self.chapter = 0 or int(input("Chapter: "))
        # Leave empty to auto-complete all sections
        # Separate sections with a comma(,)
        # ex. Sections: 1,2,3
        # to auto-complete sections 1, 2 and 3
        self.sections = [] or [
            int(section) for section in input("Sections: ").split(",")
        ]
        print(". . . success.\n")

    def login(self):
        print("Logging In . . .")
        self.driver.get(r"https://learn.zybooks.com/signin")
        WebDriverWait(self.driver, 10).until(EC.title_is("Sign in"))
        self.driver.find_element_by_id("ember10").send_keys(
            self.email)  # Email
        self.driver.find_element_by_id("ember12").send_keys(
            self.password)  # Password
        try:
            self.driver.find_element_by_class_name(
                "title").click()  # Login button
            WebDriverWait(self.driver, 10).until_not(EC.title_is("Sign in"))
        except TimeoutException:
            print(". . . failure.\n")
            os.exit()
        print(". . . success.\n")

    def select_course(self):
        print("Selecting Course . . .")
        course_selection = self.driver.find_element_by_xpath(
            f"//a[contains(@href, '{self.course}')]")
        if course_selection:
            course_selection.click()
            print(". . . success.\n")
        else:
            print(". . . failure.\n")
            os.exit()

    def select_chapter(self):
        print("Selecting Chapter . . .")
        # Grabs all the chapters in the table of contents
        chapters = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.chapter-item-controls.item-controls")))

        # Clicks chapter dropdown to show sections
        if chapters:
            chapters[self.chapter - 1].find_element_by_css_selector(
                "div.chapter-info.unused").click()
            print(". . . success.\n")
        else:
            print(". . . failure.\n")
            os.exit()

    def get_section_links(self):
        print("Getting Section Links . . .")
        sections = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH,
                 f"//a[contains(@href, 'chapter/{self.chapter}/section/')]")))
        if sections:
            self.links = [
                section.get_attribute("href") for section in sections
            ]
            if self.sections:
                dup_list = self.links.copy()
                for section in range(1, len(dup_list) + 1):
                    if section not in self.sections:
                        self.links.remove(dup_list[section - 1])

            print(". . . success.\n")
        else:
            print(". . . failure.\n")
            os._exit()

    def run(self):
        for section, link in enumerate(self.links, start=1):
            print(f"Completing Chapter {self.chapter} Section {section} . . .")
            try:
                self.driver.get(link)
                self.simulate_read(self.chapter, section)
                self.doAnimations(section)
                time.sleep(2)
                self.doMultipleChoice(section)
                time.sleep(2)
                self.doShortAnswers(section)
                time.sleep(2)
                self.doMatching(section)
                time.sleep(2)
                # self.doSelectionProblems(section) # Doesn't work
            except NoSuchElementException:
                print(". . . failed (NoSuchElement).\n")
            except Exception as ex:
                print(f". . . failed ({ex}).\n")
            print(". . . completed.\n")
            time.sleep(3)

    def close(self):
        print("Closing the program . . .")
        try:
            self.driver.close()
            self.driver.exit()
        except:
            pass
        finally:
            sys.exit(". . . success")

    @staticmethod
    def simulate_read(chapter, section):
        print(f"\t(Simulation) Reading {chapter}.{section} . . .")
        time.sleep(uniform(270.76, 390.12))
        print(f"\t. . . completed.")

    def doAnimations(self, section):
        print(f"\tDoing {self.chapter}.{section} Animations . . .")
        # 2x Speed
        two_x_buttons = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR,
                 "div.zb-checkbox.grey.label-present.right.ember-view")))
        for two_x_button in two_x_buttons:
            two_x_button.click()
            # self.driver.execute_script("arguments[0].click();", two_x_button)

        # Start animation
        start_buttons = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((
                By.CSS_SELECTOR,
                "button.zb-button.primary.false.raised.start-button.start-graphic"
            )))
        for start_button in start_buttons:
            self.driver.execute_script("arguments[0].click();", start_button)

        # Complete Animations
        continue_buttons = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "div.play-button.bounce")))
        while continue_buttons:
            for continue_button in continue_buttons:
                self.driver.execute_script("arguments[0].click();",
                                           continue_button)
            time.sleep(3)  # Abritrary time to wait for all animations to end
            try:
                continue_buttons = WebDriverWait(self.driver, 7).until(
                    EC.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "div.play-button.bounce")))
            except TimeoutException:
                break
            except:
                print("\t. . . failure.")
                return
        print("\t. . . success.")

    def doMultipleChoice(self, section):
        print(f"\tDoing {self.chapter}.{section} Multiple Choice . . .")
        mc_containers = self.driver.find_elements_by_xpath(
            "//div[@class='interactive-activity-container multiple-choice-content-resource participation large ember-view']"
        )
        mc_containers += self.driver.find_elements_by_xpath(
            "//div[@class='interactive-activity-container multiple-choice-content-resource participation medium ember-view']"
        )
        mc_containers += self.driver.find_elements_by_xpath(
            "//div[@class='interactive-activity-container multiple-choice-content-resource participation small ember-view']"
        )

        for container in mc_containers:
            questions = container.find_elements_by_xpath(
                ".//div[@class='question-set-question multiple-choice-question ember-view']"
            )
            for question in questions:
                answers = question.find_elements_by_xpath(
                    ".//label[@aria-hidden='true']")
                for answer in answers:
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView();", answer)
                    self.driver.execute_script("arguments[0].click();", answer)
                    time.sleep(uniform(0.92, 1.41))
                    if question.find_elements_by_css_selector(
                            "div.zb-explanation.has-explanation.correct"):
                        break
        print("\t. . . success.")

    def doShortAnswers(self, section):
        print(f"\tDoing {self.chapter}.{section} Short Answers . . .")
        sa_containers = self.driver.find_elements_by_xpath(
            "//div[@class='interactive-activity-container short-answer-content-resource participation large ember-view']"
        )
        sa_containers += self.driver.find_elements_by_xpath(
            "//div[@class='interactive-activity-container short-answer-content-resource participation medium ember-view']"
        )
        sa_containers += self.driver.find_elements_by_xpath(
            "//div[@class='interactive-activity-container short-answer-content-resource participation small ember-view']"
        )

        for container in sa_containers:
            questions = container.find_elements_by_xpath(
                ".//div[@class='question-set-question short-answer-question ember-view']"
            )
            for question in questions:
                # clicks on show answer button two times
                show_answer = question.find_element_by_css_selector(
                    "button.zb-button.secondary.false.show-answer-button")
                self.driver.execute_script("arguments[0].scrollIntoView();",
                                           show_answer)
                self.driver.execute_script("arguments[0].click();",
                                           show_answer)
                time.sleep(uniform(0.5, 1.2))
                self.driver.execute_script("arguments[0].scrollIntoView();",
                                           show_answer)
                self.driver.execute_script("arguments[0].click();",
                                           show_answer)

                # gets answer from box
                answer = question.find_element_by_css_selector(
                    "span.forfeit-answer").text

                # input answer into input box
                input_box = question.find_element_by_css_selector(
                    "textarea.ember-text-area.ember-view.zb-text-area.hide-scrollbar"
                )
                self.driver.execute_script("arguments[0].scrollIntoView();",
                                           input_box)
                input_box.send_keys(answer)

                # click on check button to answer question
                check_btn = question.find_element_by_css_selector(
                    "button.zb-button.primary.false.raised.check-button")
                self.driver.execute_script("arguments[0].scrollIntoView();",
                                           check_btn)
                self.driver.execute_script("arguments[0].click();", check_btn)
        print("\t. . . success.")

    def doMatching(self, section):
        print(f"\tDoing {self.chapter}.{section} Matching . . .")
        matching_containers = self.driver.find_elements_by_css_selector(
            "div.interactive-activity-container.custom-content-resource.participation.large.ember-view"
        )
        matching_containers += self.driver.find_elements_by_css_selector(
            "div.interactive-activity-container.custom-content-resource.participation.medium.ember-view"
        )
        matching_containers += self.driver.find_elements_by_css_selector(
            "div.interactive-activity-container.custom-content-resource.participation.small.ember-view"
        )
        for container in matching_containers:
            try:
                run_button = container.find_element_by_css_selector(
                    "button.run-button.zb-button.primary.raised")
                run_button.click()
            except NoSuchElementException:
                pass

            def_rows = container.find_elements_by_css_selector(
                "div.definition-row")

            for row in def_rows:
                term_bucket = row.find_element_by_css_selector(
                    "div.term-bucket")
                draggables = container.find_elements_by_css_selector(
                    "div.js-draggableObject.draggable-object.ember-view")
                for choice in draggables:
                    drag_and_drop(self.driver, choice, term_bucket)
                    time.sleep(1)
                    if row.find_elements_by_css_selector(
                            "div.definition-match-explanation.correct"):
                        break
        print("\t. . . success.")

    def doSelectionProblems(self, section):
        # Doesn't work
        print(f"\tDoing {self.chapter}.{section} Matching . . .")
        problem_containers = self.driver.find_elements_by_css_selector(
            "div.interactive-activity-container.custom-content-resource.challenge.large.ember-view"
        )
        problem_containers += self.driver.find_elements_by_css_selector(
            "div.interactive-activity-container.custom-content-resource.challenge.medium.ember-view"
        )
        problem_containers += self.driver.find_elements_by_css_selector(
            "div.interactive-activity-container.custom-content-resource.challenge.small.ember-view"
        )

        for container in problem_containers:
            start_btn = container.find_element_by_css_selector(
                "button.zyante-progression-start-button.button")
            start_btn.click()

        print("\t. . . completed.")


def main():
    # Program not work with VPN enabled
    driver = zyBooks()
    driver.login()
    driver.select_course()
    driver.select_chapter()
    driver.get_section_links()
    driver.run()
    driver.close()


if __name__ == "__main__":
    main()
