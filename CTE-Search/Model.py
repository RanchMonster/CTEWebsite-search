from DataTypes import PageData, FeedBack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from scipy.sparse import csr_matrix
import pandas as pd
from typing import List, Optional, Tuple, Any

class SearchModel:
    """A search model that combines keyword-based search with machine learning for improved results."""
    
    def __init__(self, data: List[PageData]) -> None:
        """Initialize the search model with page data.
        
        Args:
            data: List of PageData instances containing page information.
            
        Raises:
            ValueError: If data is not a list of PageData instances.
        """
        if not all(isinstance(d, PageData) for d in data):
            raise ValueError("data must be a list of PageData instances")
        
        self.__model: RandomForestRegressor = RandomForestRegressor()
        self.__df: pd.DataFrame = pd.DataFrame(data)
        self.__vectorizer: TfidfVectorizer = TfidfVectorizer(stop_words="english")
        self.__matrix: csr_matrix = self.__fit_vectorizer()
        self.__trained: bool = False
        self.__feedback_df: pd.DataFrame = pd.DataFrame(columns=['query', 'url', 'clicked'])

    def __fit_vectorizer(self) -> csr_matrix:
        """Fit the TF-IDF vectorizer on page content.
        
        Returns:
            A sparse matrix of TF-IDF features.
        """
        return self.__vectorizer.fit_transform(self.__df["content"])

    def keyword_search(self, query: str) -> np.ndarray:
        """Perform keyword-based search using cosine similarity.
        
        Args:
            query: Search query string.
            
        Returns:
            Array of similarity scores for each document.
        """
        query_vector = self.__vectorizer.transform([query])
        return cosine_similarity(query_vector, self.__matrix).flatten()

    def improved_search(self, query: str, filters: Optional[List[str]] = None) -> List[Tuple[str, str, float]]:
        """Perform improved search combining keyword search with ML-based ranking.
        
        Args:
            query: Search query string.
            filters: Optional list of filter strings to restrict results.
            
        Returns:
            List of tuples containing (url, title, rank_score) sorted by rank score.
        """
        similarities = self.keyword_search(query)
        results = []
        
        for i, sim in enumerate(similarities):
            if filters:
                page_filters = self.__df.iloc[i].get("filters", [])
                if not any(f in page_filters for f in filters):
                    continue

            features = np.array([[sim]])
            rank_score = self.__model.predict(features)[0] if self.__trained else 0
            results.append((self.__df.iloc[i]["url"], self.__df.iloc[i]["title"], rank_score))
        
        return sorted(results, key=lambda x: x[2], reverse=True)

    def append_feedback(self, query: str, picked: FeedBack) -> None:
        """Append user feedback for search results.
        
        Args:
            query: The search query that generated the results.
            picked: FeedBack instance containing user interaction data.
        """
        new_feedback = {"query": query, "url": picked.url, "clicked": int(picked.clicked)}
        self.__feedback_df = pd.concat([self.__feedback_df, pd.DataFrame([new_feedback])], ignore_index=True)
    
    def retrain(self) -> None:
        """Retrain the model using collected feedback data."""
        if self.__feedback_df.empty:
            print("No feedback data available for training.")
            return
        
        features = []
        labels = []
        for _, row in self.__feedback_df.iterrows():
            doc_index = self.__df[self.__df["url"] == row["url"]].index[0]
            similarity = self.keyword_search(row["query"])[doc_index]
            features.append([similarity])
            labels.append(row["clicked"])
        
        self.__model.fit(np.array(features), np.array(labels))
        self.__trained = True

    def __reduce__(self) -> Tuple[Any, Tuple[RandomForestRegressor, pd.DataFrame, TfidfVectorizer, csr_matrix]]:
        """Enable pickling of SearchModel instances.
        
        Returns:
            Tuple containing rebuild method and necessary arguments.
        """
        return (SearchModel.rebuild, (self.__model, self.__df, self.__vectorizer, self.__matrix))
    def append_page_data(self,new_pages:list[PageData]):
        new_df = pd.DataFrame(new_pages)
        page_titles = self.__df["title"]
        for page_title in new_df["title"]:
            for df_title in page_titles:
                if page_title == df_title:
                    raise RuntimeError(f"Invaild Page {page_title} already exist please remove old page or wipe the model to retrain")
        self.__df = pd.concat(self.__df,new_df)
        
        
    @classmethod
    def rebuild(cls, model: RandomForestRegressor, df: pd.DataFrame, 
                vectorizer: TfidfVectorizer, matrix: csr_matrix) -> 'SearchModel':
        """Rebuild a SearchModel instance from pickled data.
        
        Args:
            model: Trained RandomForestRegressor instance.
            df: DataFrame containing page data.
            vectorizer: Fitted TfidfVectorizer instance.
            matrix: TF-IDF feature matrix.
            
        Returns:
            Reconstructed SearchModel instance.
        """
        obj = cls.__new__(cls)
        obj.__df = df
        obj.__vectorizer = vectorizer
        obj.__model = model
        obj.__matrix = matrix
        obj.__trained = True
        return obj