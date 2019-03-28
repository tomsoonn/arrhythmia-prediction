# Predykcja arytmii serca za pomocą uczenia maszynowego

## Wymagania

* Python 3.6
* Tensorflow 1.8.0
* Keras 2.2.4
* wfdb 2.1.1
* PySide2 5.11.2

Dodatkowo w celu uruchomienia testów wymagana jest bibliotek pytest oraz
wtyczka pytest-qt w celu przetestowania UI.

Aby uruchomić eksperymentalne notatniki konieczna jest biblioteka Jupyter.

## Struktura

* paper - praca inżynierska
* arrhythmia - kod źródłowy:
  * arrhythmia/interface
  * arrhythmia/model
  * arrhythmia/test

## Środowisko

Wszystkie wymagane zależności znajdują się w pliku `requirements.txt`.

W celu ich zainstalowania należy użyć komendy `pip install -r requirements.txt`.

Dodatkowo zalecane jest wcześniejsze utworzenie osobnego środowiska
na przykład korzystając z narzędzia Anaconda.

# Predicting cardiac arrhythmia using machine learning
