# dictionaryindexer(under reconstruction)

This simple python script will help you index your digital dictionaries <br>
for the first release, input the pdf of your dictionary and provide a template image of what the big initial indexes look like in your book, after running the script you will receive a pdf file with all the matches in your dictionary as well as the pages where the matches were found saved as bookmarks in the pdf.
## Installation

        $ pip install requirements.txt
        $ python3 dictionaryindex.py {dictionary} {index image} {difference=30} {no. dilation iteration=3}
        
        #### dictionary: a pdf file of the dictionary
        #### index image: a screenshot of the first index in the dictionary (see example)
        #### difference: the maximum difference of compared black and white color averages, increasing this value widens the chance of getting matches
        #### no. dilation iteration: the image preprocessing function smudges the image, this is essentially the intensity of the smudge
## Usage
Open your dictionary and navigate to the first index<br>
![a](https://user-images.githubusercontent.com/98118881/155221332-41a3c7c3-4714-4ea2-8908-b6d55a4aea33.png)
<br>Screenshot the index like so, that the rectangle almost touches the box below<br>
![a](https://user-images.githubusercontent.com/98118881/155221167-44f27f96-2ae8-401c-b462-cba01928759d.jpg)
<br>Run the script<br>

        $ python3 dictionaryindex.py dict.pdf screenshot.jpg
        

