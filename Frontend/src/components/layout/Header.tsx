import { useState } from "react";
import { NavLink } from "react-router-dom";

interface HeaderProps {
  username: string;
  cargo: string;
  onLogout: () => void;
}

export default function Header({ username, cargo, onLogout }: HeaderProps) {
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-[1000] bg-[#0a1a33] text-white shadow-md">
      <div className="max-w-[1200px] mx-auto flex items-center gap-4 px-4 py-3">

        {/* LOGO + TÍTULO */}
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-xl grid place-items-center bg-gradient-to-br from-green-500 to-[#38b6ff]">
            <img
              src="/assets/cesfam.png"
              alt="CESFAM"
              className="w-full h-full object-cover rounded-full border-2 border-white/20 bg-white shadow"
            />
          </div>

          <div>
            <h1 className="text-lg font-bold leading-none">
              Intranet CESFAM Santa Rosa
            </h1>
            <p className="text-sm text-blue-100">Temuco, Chile</p>
          </div>
        </div>

        {/* NAV */}
        <nav className="ml-auto flex gap-1 bg-white/10 p-1 rounded-full text-sm">
          <NavItem to="/" icon="fa-house" label="Inicio" />
          <NavItem to="/documentos" icon="fa-file-lines" label="Documentos" />
          <NavItem to="/calendario" icon="fa-calendar" label="Calendario" />
          <NavItem to="/solicitudes" icon="fa-clock" label="Solicitudes" />
          <NavItem to="/funcionarios" icon="fa-users" label="Funcionarios" />
          <NavItem to="/licencias" icon="fa-user" label="Licencias" />
          <NavItem to="/perfil" icon="fa-user" label="" />
        </nav>

        {/* USER DROPDOWN */}
        <div className="relative">
          <button
            onClick={() => setOpen(!open)}
            className="flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-white/10 transition"
          >
            <div>
              <p className="font-semibold">{username}</p>
              <span className="text-xs text-blue-100">{cargo}</span>
            </div>
            <i className="fa-solid fa-chevron-down text-xs text-blue-100"></i>
          </button>

          {open && (
            <div className="absolute right-0 mt-2 bg-white text-gray-800 w-48 rounded-xl shadow-md p-2 animate-fade">
              <button
                onClick={onLogout}
                className="flex items-center gap-2 w-full text-left px-4 py-2 rounded-lg hover:bg-blue-100 transition"
              >
                <i className="fa-solid fa-right-from-bracket"></i>
                Cerrar sesión
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

/* ---------------------------- NAV ITEM ---------------------------- */
interface NavItemProps {
  to: string;
  icon: string;
  label: string;
}

function NavItem({ to, icon, label }: NavItemProps) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center gap-2 px-3 py-2 rounded-full transition ${
          isActive
            ? "bg-gradient-to-br from-blue-500 to-green-500 text-white shadow"
            : "text-blue-100 hover:bg-white/10"
        }`
      }
    >
      <i className={`fa-solid ${icon}`}></i>
      {label && <span>{label}</span>}
    </NavLink>
  );
}

