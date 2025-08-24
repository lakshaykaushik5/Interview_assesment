import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

type LoginFormProps = React.ComponentProps<"div"> & {
  onClickSignIn: (e: React.MouseEvent) => void;
};

export function LoginForm({
  onClickSignIn,
  className,
  ...props
  
}: LoginFormProps) {
  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card>
        <CardHeader>
          <CardTitle>IA1</CardTitle>
          <CardDescription>
            Sign In or Sign Up with you google account
          </CardDescription>
        </CardHeader>
        <CardContent>
            <div className="flex flex-col gap-6">
              <div className="flex flex-col gap-3">
                <Button variant="outline" className="w-full" onClick={onClickSignIn}>
                  Login with Google
                </Button>
              </div>
            </div>
        </CardContent>
      </Card>
    </div>
  )
}
