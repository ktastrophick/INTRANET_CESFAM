type Props = { role?: 'FUNCIONARIO' | 'DIRECCION' | 'SUBDIRECCION' };

export default function Sidebar({ role = 'FUNCIONARIO' }: Props) {
    return (
        <aside style={{ padding: 12, borderRight: '1px solid #eee', minWidth: 220 }}>
        <h4 style={{ marginTop: 0 }}>Menú {role}</h4>
        <ul style={{ paddingLeft: 18, lineHeight: 1.8 }}>
            <li>Documentos</li>
            <li>Agenda</li>
            <li>Comunicados</li>
            {role !== 'FUNCIONARIO' && <li>Gestión (solo dirección)</li>}
        </ul>
        </aside>
    );
    }
