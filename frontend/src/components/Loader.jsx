import './Loader.css';

const Loader = ({ message = 'Loading...', size = 'medium' }) => {
  return (
    <div className="loader-container">
      <div className={`loader-spinner loader-${size}`}>
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
      </div>
      {message && <p className="loader-message">{message}</p>}
    </div>
  );
};

export default Loader;
