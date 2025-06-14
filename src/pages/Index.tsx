import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { apiClient, type Department } from "@/lib/api";
import { Calendar, GraduationCap, Loader2, Users } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

const Index = () => {
  const [department, setDepartment] = useState("");
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Load departments on component mount
  useEffect(() => {
    const loadDepartments = async () => {
      try {
        setLoading(true);
        const response = await apiClient.getDepartments();
        if (response.success && response.data) {
          setDepartments(response.data);
        } else {
          toast.error('Bölümler yüklenirken hata oluştu');
        }
      } catch (error) {
        console.error('Error loading departments:', error);
        toast.error('Bölümler yüklenirken hata oluştu');
      } finally {
        setLoading(false);
      }
    };

    loadDepartments();
  }, []);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (department) {
      // Seçilen bölümü localStorage'a kaydet
      const selectedDept = departments.find(d => d.id.toString() === department);
      if (selectedDept) {
        localStorage.setItem('selectedDepartment', JSON.stringify({
          id: selectedDept.id,
          name: selectedDept.name,
          code: selectedDept.code
        }));
      }

      // Dashboard'a yönlendir
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Akıllı Sınav Planlama Sistemi</h1>
          <p className="text-gray-600">Excel ile otomatik sınav programı oluşturun</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Bölüm Seçimi</CardTitle>
            <CardDescription>
              Bölümünüzü seçin ve Excel dosyanızı yükleyerek otomatik sınav programı oluşturun
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="department">Bölüm</Label>
                <Select value={department} onValueChange={setDepartment} disabled={loading}>
                  <SelectTrigger>
                    <SelectValue placeholder={
                      loading ? "Bölümler yükleniyor..." : "Bölümünüzü seçin"
                    } />
                  </SelectTrigger>
                  <SelectContent>
                    {departments.map((dept) => (
                      <SelectItem key={dept.id} value={dept.id.toString()}>
                        {dept.name} ({dept.code})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {loading && (
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Bölümler yükleniyor...
                  </div>
                )}
              </div>

              <Button type="submit" className="w-full" disabled={!department || loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Yükleniyor...
                  </>
                ) : (
                  'Devam Et'
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="mt-8 text-center">
          <div className="flex justify-center space-x-6 text-sm text-gray-500">
            <div className="flex items-center">
              <Calendar className="h-4 w-4 mr-1" />
              Excel Yükleme
            </div>
            <div className="flex items-center">
              <Users className="h-4 w-4 mr-1" />
              Otomatik Planlama
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
