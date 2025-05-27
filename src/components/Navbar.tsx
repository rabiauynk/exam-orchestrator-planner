
import { Button } from "@/components/ui/button";
import { GraduationCap, Home, LogOut, Shield } from "lucide-react";
import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

export const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [departmentName, setDepartmentName] = useState("Bölüm");

  // localStorage'dan seçilen bölümü oku
  useEffect(() => {
    const savedDepartment = localStorage.getItem('selectedDepartment');
    if (savedDepartment) {
      try {
        const dept = JSON.parse(savedDepartment);
        setDepartmentName(dept.name);
      } catch (error) {
        console.error('Error parsing saved department:', error);
      }
    }
  }, []);

  const handleLogout = () => {
    // localStorage'ı temizle
    localStorage.removeItem('selectedDepartment');
    navigate("/");
  };

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <GraduationCap className="h-8 w-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-900">Sınav Planlama</span>
            </div>

            <div className="hidden md:flex space-x-4">
              <Button
                variant={location.pathname === "/dashboard" ? "default" : "ghost"}
                onClick={() => navigate("/dashboard")}
                className="flex items-center gap-2"
              >
                <Home className="h-4 w-4" />
                Dashboard
              </Button>
              <Button
                variant={location.pathname === "/admin" ? "default" : "ghost"}
                onClick={() => navigate("/admin")}
                className="flex items-center gap-2"
              >
                <Shield className="h-4 w-4" />
                Admin
              </Button>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600 hidden md:block">
              {departmentName}
            </span>
            <Button variant="outline" onClick={handleLogout} className="flex items-center gap-2">
              <LogOut className="h-4 w-4" />
              Çıkış
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
};
