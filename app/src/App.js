import React from 'react';
import './App.css';
import Links from './Links';

function App(props) {
  return (
    <div className="App">
        Links @ {props.url}

        <Links />
    </div>
  );
}

export default App;
