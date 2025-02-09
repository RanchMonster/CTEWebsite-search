from DataTypes import PageData,FeedBack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from scipy.sparse import csr_matrix
import pandas as pd
from typing import Optional
class SearchModel:
    """
    A search model that combines TF-IDF based keyword search with machine learning for ranking results.
    
    This class implements a hybrid search system that uses TF-IDF vectorization for initial keyword matching
    and a Random Forest model for learning from user feedback to improve search rankings.
    
    Attributes:
        __vectorizer (TfidfVectorizer): TF-IDF vectorizer for converting text to numerical features
        __model (RandomForestRegressor): Machine learning model for ranking search results
        __matrix (sparse matrix): TF-IDF matrix of the document collection
        __df (pd.DataFrame): DataFrame containing the document collection
    """
    
    def __init__(self, data: PageData,feedback:Optional[FeedBack]):
        """
        Initialize the search model with document collection.
        
        Args:
            data (PageData): Collection of documents to be indexed
            
        Raises:
            ValueError: If data is not of type PageData
        """
        if not isinstance(data, PageData,):
            raise ValueError("data must be a PageData type other data is not supported for this model")
        self.__model = RandomForestRegressor()
        self.__df = pd.DataFrame(data)
        self.__vectorizer = TfidfVectorizer(stop_words="english")
        self.__matrix = self.__fit_vectorizer()
        
    def __fit_vectorizer(self) -> object:
        """
        Fit the TF-IDF vectorizer on the document collection.
        
        Returns:
            sparse matrix: TF-IDF matrix of the document collection
        """
        return self.__vectorizer.fit_transform(self.__df["content"])
    
    def keyword_search(self, query: str) -> np.ndarray:
        """
        Perform keyword-based search using TF-IDF and cosine similarity.
        
        Args:
            query (str): Search query string
            
        Returns:
            np.ndarray: Array of similarity scores for each document
        """
        query_vector = self.__vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.__matrix).flatten()
        return similarities
    
    def learn(self, feedback_df: pd.DataFrame) -> None:
        """
        Train the ranking model using user feedback data.
        
        Args:
            feedback_df (pd.DataFrame): DataFrame containing user feedback with columns:
                                      'url', 'query', and 'clicked'
        """
        features = []
        labels = []
        for index, row in feedback_df.iterrows():
            doc_index = self.__df[self.__df["url"] == row["url"]].index[0]
            similarity = self.keyword_search(row["query"])[doc_index]
            features.append([similarity])
            labels.append(row["clicked"])  # 1 if clicked, 0 if ignored

        self.__model.fit(np.array(features), np.array(labels))
        
    def __reduce__(self):
        """
        Enable pickle serialization of the model.
        
        Returns:
            tuple: Information needed to reconstruct the object
        """
        return (SearchModel.rebuild, (self.__model, self.__df, self.__vectorizer, self.__matrix),)
    
    @classmethod
    def rebuild(cls, model: RandomForestRegressor, df: pd.DataFrame, 
                vectorizer: TfidfVectorizer, matrix: csr_matrix) -> 'SearchModel':
        """
        Reconstruct a SearchModel instance from serialized data.
        
        Args:
            model (RandomForestRegressor): Trained ranking model
            df (pd.DataFrame): Document collection
            vectorizer (TfidfVectorizer): Fitted TF-IDF vectorizer
            matrix (sparse matrix): TF-IDF matrix
            
        Returns:
            SearchModel: Reconstructed search model instance
        """
        obj = cls.__new__(cls)
        obj.__df = df
        obj.__vectorizer = vectorizer
        obj.__model = model
        obj.__matrix = matrix
        return obj