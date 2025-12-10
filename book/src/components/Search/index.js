import React, { useState, useEffect } from 'react';
import styles from './styles.module.css';

const Search = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isOpen, setIsOpen] = useState(false);

  // In a real implementation, this would connect to the backend API
  // For now, we'll simulate search with local content
  const mockSearch = async (searchQuery) => {
    // This is a placeholder - in the real implementation,
    // this would call the backend RAG API
    if (searchQuery.length < 2) {
      setResults([]);
      return;
    }

    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 300));

    // Mock results based on the query
    const mockResults = [
      { id: 1, title: `Introduction to Physical AI`, url: '/docs/foundations/01-physical-ai-embodied-intelligence', excerpt: 'Foundations of Physical AI and embodied intelligence...' },
      { id: 2, title: `ROS2 Fundamentals`, url: '/docs/ros-nervous-system/05-ros2-fundamentals', excerpt: 'Understanding the Robot Operating System version 2...' },
      { id: 3, title: `Gazebo Simulation`, url: '/docs/digital-twin/09-gazebo-basics', excerpt: 'Simulation environment for robotics development...' },
    ].filter(item =>
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.excerpt.toLowerCase().includes(searchQuery.toLowerCase())
    );

    setResults(mockResults);
  };

  useEffect(() => {
    if (query) {
      mockSearch(query);
      setIsOpen(true);
    } else {
      setResults([]);
      setIsOpen(false);
    }
  }, [query]);

  const handleSearch = (e) => {
    e.preventDefault();
    mockSearch(query);
  };

  return (
    <div className={styles.searchContainer}>
      <form onSubmit={handleSearch} className={styles.searchForm}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search textbook content..."
          className={styles.searchInput}
          onFocus={() => query && setIsOpen(true)}
        />
        <button type="submit" className={styles.searchButton}>
          🔍
        </button>
      </form>

      {isOpen && results.length > 0 && (
        <div className={styles.searchResults}>
          {results.map((result) => (
            <a
              key={result.id}
              href={result.url}
              className={styles.resultItem}
              onClick={() => {
                setQuery('');
                setIsOpen(false);
              }}
            >
              <h4 className={styles.resultTitle}>{result.title}</h4>
              <p className={styles.resultExcerpt}>{result.excerpt}</p>
            </a>
          ))}
        </div>
      )}

      {isOpen && results.length === 0 && query.length > 1 && (
        <div className={styles.noResults}>
          No results found for "{query}"
        </div>
      )}
    </div>
  );
};

export default Search;