import { ExamList } from "@/components/ExamList";
import { ExcelUpload } from "@/components/ExcelUpload";
import { ExportPanel } from "@/components/ExportPanel";
import { ExamWeekSettings } from "@/components/ExamWeekSettings";
import { Navbar } from "@/components/Navbar";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Calendar, FileSpreadsheet, Download, Settings } from "lucide-react";
import { useEffect, useState } from "react";

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState("upload");
  const [selectedDepartment, setSelectedDepartment] = useState<any>(null);

  useEffect(() => {
    // Get selected department from localStorage
    const dept = localStorage.getItem('selectedDepartment');
    if (dept) {
      setSelectedDepartment(JSON.parse(dept));
    }
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Sınav Planlama Sistemi
            {selectedDepartment && (
              <span className="text-lg font-normal text-blue-600 ml-2">
                - {selectedDepartment.name}
              </span>
            )}
          </h1>
          <p className="text-gray-600">Excel dosyası yükleyerek otomatik sınav programı oluşturun</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 lg:w-[600px]">
            <TabsTrigger value="upload" className="flex items-center gap-2">
              <FileSpreadsheet className="h-4 w-4" />
              Excel Yükle
            </TabsTrigger>
            <TabsTrigger value="schedule" className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Sınav Programı
            </TabsTrigger>
            <TabsTrigger value="export" className="flex items-center gap-2">
              <Download className="h-4 w-4" />
              Excel İndir
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Ayarlar
            </TabsTrigger>
          </TabsList>

          <TabsContent value="upload">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileSpreadsheet className="h-5 w-5" />
                  Excel ile Toplu Sınav Ekleme
                </CardTitle>
                <CardDescription>
                  Excel dosyanızı yükleyin, sistem otomatik olarak zorluk seviyesi ve sınav süresine göre en uygun programı oluşturacak
                </CardDescription>
              </CardHeader>
              <CardContent>
                {selectedDepartment ? (
                  <ExcelUpload
                    departmentId={selectedDepartment.id}
                    onUploadComplete={(result) => {
                      // Switch to schedule tab after successful upload
                      if (result.success) {
                        setActiveTab("schedule");
                      }
                    }}
                  />
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    Lütfen önce bir bölüm seçin
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="schedule">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  Oluşturulan Sınav Programı
                </CardTitle>
                <CardDescription>
                  Otomatik olarak oluşturulan sınav programınızı görüntüleyin
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ExamList />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="export">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Download className="h-5 w-5" />
                  Excel Dışa Aktarım
                </CardTitle>
                <CardDescription>
                  Sınav programınızı Excel formatında indirin
                </CardDescription>
              </CardHeader>
              <CardContent>
                {selectedDepartment ? (
                  <ExportPanel />
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    Lütfen önce bir bölüm seçin
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  Sınav Haftası Ayarları
                </CardTitle>
                <CardDescription>
                  Sınav haftası tarihlerini belirleyin
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ExamWeekSettings />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Dashboard;
