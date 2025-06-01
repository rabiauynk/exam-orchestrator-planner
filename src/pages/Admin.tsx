import { ExamList } from "@/components/ExamList";
import { ExamWeekSettings } from "@/components/ExamWeekSettings";
import { ExcelUpload } from "@/components/ExcelUpload";
import { ExportPanel } from "@/components/ExportPanel";
import { Navbar } from "@/components/Navbar";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { apiClient } from "@/lib/api";
import { BarChart3, Download, FileSpreadsheet, List, Settings } from "lucide-react";
import { useEffect, useState } from "react";

const Admin = () => {
  const [stats, setStats] = useState({
    totalExams: 0,
    plannedExams: 0,
    pendingExams: 0
  });

  // Load statistics
  useEffect(() => {
    const loadStats = async () => {
      try {
        const response = await apiClient.getExams();
        if (response.success && response.data) {
          const exams = response.data;
          const planned = exams.filter(exam => exam.status === 'planned').length;
          const pending = exams.filter(exam => exam.status === 'pending').length;

          setStats({
            totalExams: exams.length,
            plannedExams: planned,
            pendingExams: pending
          });
        }
      } catch (error) {
        console.error('Error loading statistics:', error);
      }
    };

    loadStats();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Admin Paneli</h1>
          <p className="text-gray-600">Tüm sınavları yönetin ve planlamaları dışa aktarın</p>
        </div>

        <Tabs defaultValue="exams" className="space-y-6">
          <TabsList className="grid w-full grid-cols-5 lg:w-[600px]">
            <TabsTrigger value="exams" className="flex items-center gap-2">
              <List className="h-4 w-4" />
              Sınavlar
            </TabsTrigger>
            <TabsTrigger value="excel" className="flex items-center gap-2">
              <FileSpreadsheet className="h-4 w-4" />
              Excel
            </TabsTrigger>
            <TabsTrigger value="export" className="flex items-center gap-2">
              <Download className="h-4 w-4" />
              Dışa Aktar
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Ayarlar
            </TabsTrigger>
            <TabsTrigger value="stats" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              İstatistikler
            </TabsTrigger>
          </TabsList>

          <TabsContent value="exams">
            <Card>
              <CardHeader>
                <CardTitle>Tüm Sınavlar</CardTitle>
                <CardDescription>
                  Sisteme eklenen tüm sınavları görüntüleyin ve yönetin
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ExamList />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="excel">
            <Card>
              <CardHeader>
                <CardTitle>Excel ile Toplu Sınav Ekleme</CardTitle>
                <CardDescription>
                  Excel dosyası yükleyerek birden fazla sınavı aynı anda sisteme ekleyin ve otomatik planlama yapın
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ExcelUpload
                  departmentId={1}
                  onUploadComplete={(result) => {
                    // Refresh stats after upload
                    window.location.reload();
                  }}
                />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="export">
            <Card>
              <CardHeader>
                <CardTitle>Excel Dışa Aktarım</CardTitle>
                <CardDescription>
                  Her bölüm için ayrı sekmeli Excel dosyası oluşturun
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ExportPanel />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings">
            <Card>
              <CardHeader>
                <CardTitle>Sistem Ayarları</CardTitle>
                <CardDescription>
                  Sınav planlama sistemi için genel ayarları yapın
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ExamWeekSettings />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="stats">
            <Card>
              <CardHeader>
                <CardTitle>İstatistikler</CardTitle>
                <CardDescription>
                  Sınav dağılımı ve planlama verimliliği
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <h3 className="font-semibold text-blue-900">Toplam Sınav</h3>
                    <p className="text-2xl font-bold text-blue-600">{stats.totalExams}</p>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg">
                    <h3 className="font-semibold text-green-900">Planlanmış</h3>
                    <p className="text-2xl font-bold text-green-600">{stats.plannedExams}</p>
                  </div>
                  <div className="p-4 bg-orange-50 rounded-lg">
                    <h3 className="font-semibold text-orange-900">Beklemede</h3>
                    <p className="text-2xl font-bold text-orange-600">{stats.pendingExams}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Admin;
