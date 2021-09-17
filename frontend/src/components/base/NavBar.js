import '../../css/navbar.css';
import { Link } from 'react-router-dom';

function NavBar(props) {
    return (
        <header className="nav-header">
            <h1 className="logo"><Link to="/">HRPYML</Link></h1>
            <input type="checkbox" id="nav-toggle" className="nav-toggle" />
            <label htmlFor="nav-toggle" className="nav-toggle-label">
                <span></span>
            </label>
            <nav>
                <ul>
                    <li><Link to="/">Train Network</Link></li>
                    {/* <li><Link to="/about">About</Link></li> */}
                    <li><a href="https://github.com/Haydn-Robinson/Python-Machine-Learning">HR-PYML</a></li>
                    <li><a href="https://github.com/Haydn-Robinson/Neural-Network-Web-App">Source Code</a></li>
                </ul>
            </nav>
        </header>
        
    )
}

export default NavBar;