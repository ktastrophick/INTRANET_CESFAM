import { Link } from "react-router-dom";

export default function Nav() {
    return (
        <nav style={{ padding: 8, borderBottom: '1px dashed #eee' }}>
        <Link to="/" style={{ marginRight: 12 }}>Inicio</Link>
        <Link to="/funcionarios" style={{ marginRight: 12 }}>Funcionarios</Link>
        <Link to="/direccion" style={{ marginRight: 12 }}>Dirección</Link>
        <Link to="/subdireccion">Subdirección</Link>
        </nav>
    );
}
