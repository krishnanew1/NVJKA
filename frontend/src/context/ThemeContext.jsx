import { createContext, useContext, useState, useEffect } from 'react';

// Create the Theme Context
const ThemeContext = createContext();

// Custom hook to use the theme context
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// Theme Provider Component
export const ThemeProvider = ({ children }) => {
  // Always use dark theme
  const [theme] = useState('dark');

  // Apply dark theme to document element
  useEffect(() => {
    // Apply dark theme to document
    document.documentElement.setAttribute('data-theme', 'dark');
    
    // Add theme class to body for additional styling
    document.body.className = 'theme-dark';
  }, []);

  // Context value - keeping the same API for compatibility
  const value = {
    theme: 'dark',
    isDark: true,
    toggleTheme: () => {}, // No-op function for compatibility
    setThemeMode: () => {}, // No-op function for compatibility
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export default ThemeContext;