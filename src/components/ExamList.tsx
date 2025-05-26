
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Calendar, Clock, Users, Computer, Trash2 } from "lucide-react";

// Örnek veri
const mockExams = [
  {
    id: 1,
    courseName: "Veri Yapıları",
    className: "2",
    studentCount: 45,
    duration: 120,
    needsComputer: true,
    preferredDates: ["15/01/2024", "17/01/2024", "19/01/2024"],
    status: "planned",
    scheduledDate: "16/01/2024",
    scheduledTime: "09:00-11:00",
    room: "BM-201"
  },
  {
    id: 2,
    courseName: "Calculus I",
    className: "1",
    studentCount: 60,
    duration: 90,
    needsComputer: false,
    preferredDates: ["16/01/2024", "18/01/2024", "20/01/2024"],
    status: "pending",
    scheduledDate: null,
    scheduledTime: null,
    room: null
  },
  {
    id: 3,
    courseName: "Yazılım Mühendisliği",
    className: "3",
    studentCount: 35,
    duration: 150,
    needsComputer: true,
    preferredDates: ["18/01/2024", "20/01/2024", "22/01/2024"],
    status: "planned",
    scheduledDate: "19/01/2024",
    scheduledTime: "14:00-16:30",
    room: "BM-Lab1"
  }
];

export const ExamList = () => {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case "planned":
        return <Badge variant="default" className="bg-green-500">Planlandı</Badge>;
      case "pending":
        return <Badge variant="secondary">Beklemede</Badge>;
      default:
        return <Badge variant="outline">Bilinmiyor</Badge>;
    }
  };

  return (
    <div className="space-y-4">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Ders</TableHead>
              <TableHead>Sınıf</TableHead>
              <TableHead>Öğrenci</TableHead>
              <TableHead>Süre</TableHead>
              <TableHead>Bilgisayar</TableHead>
              <TableHead>Durum</TableHead>
              <TableHead>Planlanmış</TableHead>
              <TableHead>İşlemler</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {mockExams.map((exam) => (
              <TableRow key={exam.id}>
                <TableCell className="font-medium">{exam.courseName}</TableCell>
                <TableCell>{exam.className}. Sınıf</TableCell>
                <TableCell>
                  <div className="flex items-center gap-1">
                    <Users className="h-4 w-4" />
                    {exam.studentCount}
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-1">
                    <Clock className="h-4 w-4" />
                    {exam.duration} dk
                  </div>
                </TableCell>
                <TableCell>
                  {exam.needsComputer ? (
                    <Computer className="h-4 w-4 text-blue-600" />
                  ) : (
                    <span className="text-gray-400">-</span>
                  )}
                </TableCell>
                <TableCell>{getStatusBadge(exam.status)}</TableCell>
                <TableCell>
                  {exam.status === "planned" ? (
                    <div className="space-y-1">
                      <div className="flex items-center gap-1 text-sm">
                        <Calendar className="h-3 w-3" />
                        {exam.scheduledDate}
                      </div>
                      <div className="flex items-center gap-1 text-sm text-gray-600">
                        <Clock className="h-3 w-3" />
                        {exam.scheduledTime}
                      </div>
                      <div className="text-xs text-gray-500">{exam.room}</div>
                    </div>
                  ) : (
                    <span className="text-gray-400">Planlanmadı</span>
                  )}
                </TableCell>
                <TableCell>
                  <Button variant="outline" size="sm">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      
      {mockExams.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          Henüz sınav eklenmedi. Yeni sınav eklemek için "Sınav Ekle" sekmesini kullanın.
        </div>
      )}
    </div>
  );
};
