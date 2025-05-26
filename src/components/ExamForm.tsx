
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { format } from "date-fns";
import { CalendarIcon, Plus, X } from "lucide-react";
import { cn } from "@/lib/utils";

export const ExamForm = () => {
  const [courseName, setCourseName] = useState("");
  const [className, setClassName] = useState("");
  const [studentCount, setStudentCount] = useState("");
  const [duration, setDuration] = useState("");
  const [needsComputer, setNeedsComputer] = useState(false);
  const [preferredDates, setPreferredDates] = useState<Date[]>([]);
  const [notes, setNotes] = useState("");

  const addPreferredDate = (date: Date | undefined) => {
    if (date && preferredDates.length < 3 && !preferredDates.some(d => d.getTime() === date.getTime())) {
      setPreferredDates([...preferredDates, date]);
    }
  };

  const removePreferredDate = (index: number) => {
    setPreferredDates(preferredDates.filter((_, i) => i !== index));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Form verilerini işle
    console.log({
      courseName,
      className,
      studentCount: parseInt(studentCount),
      duration: parseInt(duration),
      needsComputer,
      preferredDates,
      notes
    });
    
    // Form temizle
    setCourseName("");
    setClassName("");
    setStudentCount("");
    setDuration("");
    setNeedsComputer(false);
    setPreferredDates([]);
    setNotes("");
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="courseName">Ders Adı</Label>
          <Input
            id="courseName"
            value={courseName}
            onChange={(e) => setCourseName(e.target.value)}
            placeholder="Ders adını girin"
            required
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="className">Sınıf</Label>
          <Select value={className} onValueChange={setClassName}>
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
        <Label>Tercih Edilen Tarihler (En fazla 3)</Label>
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
        
        {preferredDates.length < 3 && (
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
                Tarih ekle
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
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="notes">Notlar (İsteğe bağlı)</Label>
        <Textarea
          id="notes"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Ek notlar..."
          className="min-h-[80px]"
        />
      </div>

      <Button type="submit" className="w-full">
        <Plus className="mr-2 h-4 w-4" />
        Sınav Ekle
      </Button>
    </form>
  );
};
