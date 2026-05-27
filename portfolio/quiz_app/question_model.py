"""
=============================================================
  question_model.py — Quiz App
  Student:   Bart Brondeel
  Opleiding: Graduaat Programmeren - Odisee

  Beschrijving:
  ------------
  Bevat de Question klasse.
  Een Question object stelt één quizvraag voor,
  met de bijbehorende tekst en het juiste antwoord.
=============================================================
"""


class Question:
    """
    Stelt één quizvraag voor met tekst en antwoord.

    Attributen:
    -----------
    text   (str) : De tekst van de vraag
    answer (str) : Het correcte antwoord ("True" of "False")
    """

    def __init__(self, question_text: str, question_answer: str):
        """
        Maakt een nieuw Question object aan.

        Parameters:
        -----------
        question_text   : De tekst van de vraag
        question_answer : "True" of "False"
        """
        self.text = question_text
        self.answer = question_answer
