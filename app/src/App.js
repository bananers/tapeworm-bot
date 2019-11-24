import React from 'react';
import './App.css';
import Links from './Links';
import { Header, Container, Image } from 'semantic-ui-react'

function App(props) {
  return (
    <div className="App">

      <Container>
      <Header size='huge'>
        <Image circular src='/images/tapeworm-icon.png'  size='massive' style={{marginTop: "40px"}}/>
        <Header.Content style={{marginTop: "40px"}}>
          Links @ {props.url}
        </Header.Content>
      </Header>

      <Links />

      </Container>
    </div>
  );
}

export default App;
