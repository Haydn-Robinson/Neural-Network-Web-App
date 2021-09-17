import '../../css/App.css';
import NavBar from './NavBar.js'
import TrainNetwork from './../pages/TrainNetwork.js'
import About from './../pages/About.js'
import PageNotFound from './../pages/PageNotFound.js'
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';

function App() {
  return (
    <Router>
      <NavBar/>
      <main>
          <Switch>
              <Route path="/" exact component={TrainNetwork}/>
              <Route path="/trainnetwork" exact component={TrainNetwork}/>
              <Route path="/about" component={About}/>
              <Route path='/' component={PageNotFound}/>
          </Switch>
      </main>
    </Router>
  )
}

export default App;
