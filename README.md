# FashionIsta

## Problem Statement
<p align='justify'>
* Recommendation systems have been an essential part of company infrastructure and sales techniques for quite some time, which in cases has led to economic- as well as technological growth. 
* Google, Netflix, Amazon and Spotify are a handful of well-known companies famous for their recommendation systems and their technological- and economical growth. 
* A recommendation system today is a broad subject and can, on a high abstraction level, be divided into different areas with different implementations for different occasions.
* In today's dynamic world of technology and in the face of this pandemic, it's critical for a growing e-commerce company to engage its customers and ensure their shopping safety.Instead of physical shopping, we are encouraging users to shop for their favourite items on a single site, and recommending those relevant items to them is more impressive and offers a greater sense of satisfaction.
</p>

## Data Collection

<p align='justify'>
  <img src="https://github.com/AkshitTayade/FashionIsta/blob/master/static/images/Picture%201.png">
</p>

<p align='justify'>
To get eclectic clothing apparel, we used the unique dataset available at [Kaggle]() which contains fashion apparel such as shoes, heels, rings, clothes. This dataset had a range of fashion apparel, but we made use of only clothing apparel for males and females. The dataset comes with a text file containing fields like brand name, product name, product type, label, image file. By the use of column: product type, we eliminate those items rows that were not needed. After removing unnecessary fashion apparel, our database had cleaned and essential clothing images. We also used the Large-scale apparel dataset which was fetched from [DeepFashion Database]().
</p>

## Model Architecture

<p align="justify">
  <img src="https://github.com/AkshitTayade/FashionIsta/blob/master/static/images/Picture%202.png">
</p>

<p align='justify'>
### Feature Extractor
The feature extraction model will extract all rich information from the image as features. Our initial approach was to detect as many features as possible from a given image using CNN.We choose a pre-trained VGG16. As we just wanted to extract rich features from a pre- trained model and not do prediction/classification problems with our dataset, VGG16’s prediction layer was not needed (i.e., output layer). Considering VGG weights size and training time, it took a huge training time.

### Cosine Similarity 
We then use the concept of similarity on our predicated array obtained from the VGG16 model. A particular image’s predicted array is cosine with the rest images array. This generates a 2D matrix containing similarity scores of one vs rest images. Then the cosine similarity matrix is converted into a data frame.

**The Visual Similarity model is implemented on “Web application”. Once the image is passed through the data frame created by the “cosine similarity model”, we get a 1D array containing similarity scores with respect to other images in the database. This 1D array is sorted descending, giving top scores at the beginning of an array. From this sorted 1d array, we choose the top ‘n’ results we want.**
</p>

## Tech Stack
1. Bootstrap (Frontend)
2. Flask (Backend)
3. Flask- SQLalchemy (Database)
4. BeautifulSoup (WebScraping)
5. Razorpay (Payment Integration)
6. Github (Version Control)
7. Visual Studio Code (Code Editor)
8. Heroku (Deployment)

## Future Scope
* This project currently runs on local storage, but it can be transferred to cloud storage like IMGUR, AWS, AZURE, Cloudinary for unlimited storage and faster website loading. 
* More features like User can upload his desired clothing item on our website, and get similar items and have specific search results; Full duplex portal, where Organisation can upload their clothing apparels anytime they want, and changes are reflected towards user side too.

## Video link for demo
[Video Link](https://www.youtube.com/watch?v=fnF34vbAv9s)
