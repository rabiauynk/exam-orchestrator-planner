
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { format } from "date-fns";
import { CalendarIcon, Plus, X } from "lucide-react";
import { cn } from "@/lib/utils";

// Bölümlere göre dersler
const coursesByDepartment = {
  "1": [
    "Matematik I",
    "Fizik I", 
    "Kimya I",
    "Mühendislik Temelleri",
    "Türk Dili I"
  ],
  "2": [
    "Matematik II",
    "Fizik II",
    "Kimya II", 
    "Mühendislik Matematik I",
    "Türk Dili II"
  ],
  "3": [
    "Diferansiyel Denklemler",
    "Termodinamik",
    "Malzeme Bilimi",
    "Mühendislik Matematik II",
    "İstatistik"
  ],
  "4": [
    "Bitirme Projesi I",
    "Bitirme Projesi II",
    "Endüstriyel Uygulamalar",
    "Proje Yönetimi",
    "Meslek Etiği"
  ]
};

export const ExamForm = () => {
  const [courseName, setCourseName] = useState("");
  const [className, setClassName] = useState("");
  const [studentCount, setStudentCount] = useState("");
  const [duration, setDuration] = useState("");
  const [needsComputer, setNeedsComputer] = useState(false);
  const [preferredDates, setPreferredDates] = useState<Date[]>([]);

  const addPreferredDate = (date: Date | undefined) => {
    if (date && !preferredDates.some(d => d.getTime() === date.getTime())) {
      setPreferredDates([...preferredDates, date]);
    }
  };

  const removePreferredDate = (index: number) => {
    setPreferredDates(preferredDates.filter((_, i) => i !== index));
  };

  const handleClassChange = (value: string) => {
    setClassName(value);
    setCourseName(""); // Sınıf değiştiğinde ders seçimini sıfırla
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (preferredDates.length < 3) {
      alert("En az 3 tercih edilen tarih seçmelisiniz!");
      return;
    }
    
    // Form verilerini işle
    console.log({
      courseName,
      className,
      studentCount: parseInt(studentCount),
      duration: parseInt(duration),
      needsComputer,
      preferredDates
    });
    
    // Form temizle
    setCourseName("");
    setClassName("");
    setStudentCount("");
    setDuration("");
    setNeedsComputer(false);
    setPreferredDates([]);
  };

  // Seçilen sınıfa göre dersleri getir
  const availableCourses = className ? coursesByDepartment[className as keyof typeof coursesByDepartment] || [] : [];

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="className">Sınıf</Label>
          <Select value={className} onValueChange={handleClassChange}>
            <SelectTrigger>
              <SelectValue placeholder="Sınıf seçin" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">1. Sınıf</SelectItem>
              <SelectItem value="2">2. Sınıf</SelectItem>
              <SelectItem value="3">3. Sınıf</SelectItem>
              <SelectItem value="4">4. Sınıf</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="courseName">Ders Adı</Label>
          <Select value={courseName} onValueChange={setCourseName} disabled={!className}>
            <SelectTrigger>
              <SelectValue placeholder={className ? "Ders seçin" : "Önce sınıf seçin"} />
            </SelectTrigger>
            <SelectContent>
              {availableCourses.map((course) => (
                <SelectItem key={course} value={course}>
                  {course}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="studentCount">Öğrenci Sayısı</Label>
          <Input
            id="studentCount"
            type="number"
            value={studentCount}
            onChange={(e) => setStudentCount(e.target.value)}
            placeholder="Öğrenci sayısını girin"
            min="1"
            required
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="duration">Süre (dakika)</Label>
          <Input
            id="duration"
            type="number"
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
            placeholder="Sınav süresi"
            min="30"
            step="30"
            required
          />
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <Switch
          id="needsComputer"
          checked={needsComputer}
          onCheckedChange={setNeedsComputer}
        />
        <Label htmlFor="needsComputer">Bilgisayar İhtiyacı Var</Label>
      </div>

      <div className="space-y-3">
        <Label>Tercih Edilen Tarihler (En az 3 tarih seçin)</Label>
        <div className="flex flex-wrap gap-2">
          {preferredDates.map((date, index) => (
            <div key={index} className="flex items-center gap-2 bg-blue-50 px-3 py-1 rounded-md">
              <span className="text-sm">{format(date, "dd/MM/yyyy")}</span>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => removePreferredDate(index)}
                className="h-auto p-0 hover:bg-transparent"
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          ))}
        </div>
        
        <Popover>
          <PopoverTrigger asChild>
            <Button
              type="button"
              variant="outline"
              className={cn(
                "justify-start text-left font-normal",
                "text-muted-foreground"
              )}
            >
              <CalendarIcon className="mr-2 h-4 w-4" />
              Tarih ekle ({preferredDates.length} seçili)
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0" align="start">
            <Calendar
              mode="single"
              onSelect={addPreferredDate}
              disabled={(date) => date < new Date()}
              initialFocus
              className="pointer-events-auto"
            />
          </PopoverContent>
        </Popover>
        
        {preferredDates.length < 3 && (
          <p className="text-sm text-red-600">
            En az 3 tercih edilen tarih seçmelisiniz. (Şu an: {preferredDates.length})
          </p>
        )}
      </div>

      <Button type="submit" className="w-full" disabled={preferredDates.length < 3}>
        <Plus className="mr-2 h-4 w-4" />
        Sınav Ekle
      </Button>
    </form>
  );
};
