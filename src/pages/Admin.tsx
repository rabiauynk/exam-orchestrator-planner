
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Navbar } from "@/components/Navbar";
import { ExamSchedule } from "@/components/ExamSchedule";
import { ExportPanel } from "@/components/ExportPanel";
import { ExamWeekSettings } from "@/components/ExamWeekSettings";
import { Calendar, Download, Settings, BarChart3 } from "lucide-react";

const Admin = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Admin Paneli</h1>
          <p className="text-gray-600">Tüm sınavları yönetin ve planlamaları dışa aktarın</p>
        </div>

        <Tabs defaultValue="schedule" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 lg:w-[500px]">
            <TabsTrigger value="schedule" className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Planlama
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

          <TabsContent value="schedule">
            <Card>
              <CardHeader>
                <CardTitle>Sınav Programı</CardTitle>
                <CardDescription>
                  Tüm bölümlerden gelen sınavların otomatik planlaması
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ExamSchedule />
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
                    <p className="text-2xl font-bold text-blue-600">24</p>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg">
                    <h3 className="font-semibold text-green-900">Planlanmış</h3>
                    <p className="text-2xl font-bold text-green-600">20</p>
                  </div>
                  <div className="p-4 bg-orange-50 rounded-lg">
                    <h3 className="font-semibold text-orange-900">Beklemede</h3>
                    <p className="text-2xl font-bold text-orange-600">4</p>
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
