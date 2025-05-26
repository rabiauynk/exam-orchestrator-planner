
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Download, FileSpreadsheet, Calendar } from "lucide-react";

// Örnek departman verisi
const departments = [
  {
    name: "Bilgisayar Mühendisliği",
    examCount: 8,
    lastUpdate: "15/01/2024 14:30"
  },
  {
    name: "Elektrik-Elektronik Mühendisliği",
    examCount: 6,
    lastUpdate: "15/01/2024 12:15"
  },
  {
    name: "Makine Mühendisliği",
    examCount: 5,
    lastUpdate: "15/01/2024 11:45"
  },
  {
    name: "İnşaat Mühendisliği",
    examCount: 4,
    lastUpdate: "15/01/2024 10:30"
  },
  {
    name: "Endüstri Mühendisliği",
    examCount: 3,
    lastUpdate: "15/01/2024 09:20"
  }
];

export const ExportPanel = () => {
  const handleExportAll = () => {
    // Tüm bölümler için Excel oluştur
    console.log("Exporting all departments...");
  };

  const handleExportDepartment = (departmentName: string) => {
    // Belirli bölüm için Excel oluştur
    console.log(`Exporting ${departmentName}...`);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold">Excel Dışa Aktarım</h3>
          <p className="text-gray-600">Her bölüm için ayrı sekmeli Excel dosyası oluşturun</p>
        </div>
        <Button onClick={handleExportAll} className="flex items-center gap-2">
          <Download className="h-4 w-4" />
          Tümünü Dışa Aktar
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {departments.map((dept, index) => (
          <Card key={index}>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">{dept.name}</CardTitle>
              <CardDescription className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                <Badge variant="secondary">{dept.examCount} sınav</Badge>
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="text-sm text-gray-600">
                Son güncelleme: {dept.lastUpdate}
              </div>
              <Button 
                variant="outline" 
                size="sm" 
                className="w-full flex items-center gap-2"
                onClick={() => handleExportDepartment(dept.name)}
              >
                <FileSpreadsheet className="h-4 w-4" />
                Excel Oluştur
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Dışa Aktarım Ayarları</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="text-sm">
              <strong>Excel Formatı:</strong> Her bölüm ayrı sekme olarak
            </div>
            <div className="text-sm">
              <strong>İçerik:</strong> Sınav tarihi, saati, ders adı, sınıf, öğrenci sayısı, süre, sınıf/lab bilgisi
            </div>
            <div className="text-sm">
              <strong>Sıralama:</strong> Tarih ve saate göre kronolojik
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
