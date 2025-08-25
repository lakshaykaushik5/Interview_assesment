import React, { createContext, useState, useContext } from "react";

const NavbarContext = createContext({
  onNavbarClick: () => {},
  setOnNavbarClick: (f: () => void) => {},
});

export const NavbarProvider = ({ children }: { children: React.ReactNode }) => {
  const [onNavbarClick, setOnNavbarClick] = useState(() => () => {});

  return (
    <NavbarContext.Provider value={{ onNavbarClick, setOnNavbarClick }}>
      {children}
    </NavbarContext.Provider>
  );
};

export const useNavbarContext = () => useContext(NavbarContext);
