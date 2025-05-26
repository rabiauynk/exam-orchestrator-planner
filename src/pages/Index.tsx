
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { GraduationCap, Calendar, Users } from "lucide-react";

const Index = () => {
  const [department, setDepartment] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const departments = [
    "Bilgisayar Mühendisliği",
    "Elektrik-Elektronik Mühendisliği", 
    "Makine Mühendisliği",
    "İnşaat Mühendisliği",
    "Endüstri Mühendisliği"
  ];

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (department && password) {
      // Basit giriş kontrolü - gerçek uygulamada Supabase auth kullanılacak
      navigate("/dashboard");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-blue-600 rounded-full">
              <GraduationCap className="h-8 w-8 text-white" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Sınav Planlama Sistemi</h1>
          <p className="text-gray-600">Öğretim üyesi girişi</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Giriş Yap</CardTitle>
            <CardDescription>
              Bölümünüzü seçin ve şifrenizi girin
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="department">Bölüm</Label>
                <Select value={department} onValueChange={setDepartment}>
                  <SelectTrigger>
                    <SelectValue placeholder="Bölümünüzü seçin" />
                  </SelectTrigger>
                  <SelectContent>
                    {departments.map((dept) => (
                      <SelectItem key={dept} value={dept}>
                        {dept}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Şifre</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Şifrenizi girin"
                  required
                />
              </div>

              <Button type="submit" className="w-full" disabled={!department || !password}>
                Giriş Yap
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="mt-8 text-center">
          <div className="flex justify-center space-x-6 text-sm text-gray-500">
            <div className="flex items-center">
              <Calendar className="h-4 w-4 mr-1" />
              Sınav Planlama
            </div>
            <div className="flex items-center">
              <Users className="h-4 w-4 mr-1" />
              Sınıf Yönetimi
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
