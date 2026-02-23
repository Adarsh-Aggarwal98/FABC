import { useState, useEffect } from "react";
import { Link } from "wouter";
import { useAuth, authFetch } from "@/contexts/AuthContext";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Users, UserPlus, Clock, CheckCircle, XCircle, Mail, Loader2, Shield, ArrowLeft, FileText, Bell, Plus, Pencil, Trash2 } from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  phone?: string;
  role: string;
  status: string;
  createdAt: string;
  lastLoginAt?: string;
}

interface Invitation {
  id: string;
  email: string;
  role: string;
  createdAt: string;
  expiresAt: string;
}

interface Blog {
  id: string;
  title: string;
  slug: string;
  excerpt: string;
  content?: string;
  category: string;
  author: string;
  readTime: string;
  image?: string;
  featured: boolean;
  published: boolean;
  createdAt: string;
  updatedAt?: string;
}

interface AtoAlert {
  id: string;
  title: string;
  type: "update" | "alert" | "reminder";
  link: string;
  active: boolean;
  priority: number;
  createdAt: string;
  expiresAt?: string;
}

export default function AdminDashboard() {
  const { user } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [pendingUsers, setPendingUsers] = useState<User[]>([]);
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [blogs, setBlogs] = useState<Blog[]>([]);
  const [atoAlerts, setAtoAlerts] = useState<AtoAlert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Invite form state
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState<"user" | "accountant">("user");
  const [isInviting, setIsInviting] = useState(false);
  const [inviteDialogOpen, setInviteDialogOpen] = useState(false);

  // Blog form state
  const [blogDialogOpen, setBlogDialogOpen] = useState(false);
  const [editingBlog, setEditingBlog] = useState<Blog | null>(null);
  const [blogForm, setBlogForm] = useState({
    title: "",
    slug: "",
    excerpt: "",
    content: "",
    category: "",
    author: "",
    readTime: "5 min read",
    image: "",
    featured: false,
    published: true,
  });

  // ATO Alert form state
  const [alertDialogOpen, setAlertDialogOpen] = useState(false);
  const [editingAlert, setEditingAlert] = useState<AtoAlert | null>(null);
  const [alertForm, setAlertForm] = useState({
    title: "",
    type: "update" as "update" | "alert" | "reminder",
    link: "",
    active: true,
    priority: 0,
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [usersRes, pendingRes, invitationsRes, blogsRes, alertsRes] = await Promise.all([
        authFetch("/api/admin/users"),
        authFetch("/api/admin/users/pending"),
        authFetch("/api/admin/invitations"),
        authFetch("/api/admin/blogs"),
        authFetch("/api/admin/ato-alerts"),
      ]);

      if (usersRes.ok) setUsers(await usersRes.json());
      if (pendingRes.ok) setPendingUsers(await pendingRes.json());
      if (invitationsRes.ok) setInvitations(await invitationsRes.json());
      if (blogsRes.ok) setBlogs(await blogsRes.json());
      if (alertsRes.ok) setAtoAlerts(await alertsRes.json());
    } catch (error) {
      console.error("Failed to fetch data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = async (userId: string) => {
    try {
      const response = await authFetch(`/api/admin/users/${userId}/approve`, { method: "POST" });

      if (response.ok) {
        setSuccess("User approved successfully");
        fetchData();
      } else {
        const data = await response.json();
        setError(data.error || "Failed to approve user");
      }
    } catch (error) {
      setError("Network error");
    }
  };

  const handleReject = async (userId: string) => {
    if (!confirm("Are you sure you want to reject this user?")) return;

    try {
      const response = await authFetch(`/api/admin/users/${userId}/reject`, { method: "POST" });

      if (response.ok) {
        setSuccess("User rejected");
        fetchData();
      } else {
        setError("Failed to reject user");
      }
    } catch (error) {
      setError("Network error");
    }
  };

  const handleSuspend = async (userId: string) => {
    if (!confirm("Are you sure you want to suspend this user?")) return;

    try {
      const response = await authFetch(`/api/admin/users/${userId}/suspend`, { method: "POST" });

      if (response.ok) {
        setSuccess("User suspended");
        fetchData();
      } else {
        setError("Failed to suspend user");
      }
    } catch (error) {
      setError("Network error");
    }
  };

  const handleReactivate = async (userId: string) => {
    try {
      const response = await authFetch(`/api/admin/users/${userId}/reactivate`, { method: "POST" });

      if (response.ok) {
        setSuccess("User reactivated");
        fetchData();
      } else {
        setError("Failed to reactivate user");
      }
    } catch (error) {
      setError("Network error");
    }
  };

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsInviting(true);
    setError("");

    try {
      const response = await authFetch("/api/admin/invite", {
        method: "POST",
        body: JSON.stringify({ email: inviteEmail, role: inviteRole }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess("Invitation sent successfully");
        setInviteDialogOpen(false);
        setInviteEmail("");
        setInviteRole("user");
        fetchData();
      } else {
        setError(data.error || "Failed to send invitation");
      }
    } catch (error) {
      setError("Network error");
    } finally {
      setIsInviting(false);
    }
  };

  const handleCancelInvitation = async (invitationId: string) => {
    try {
      const response = await authFetch(`/api/admin/invitations/${invitationId}`, { method: "DELETE" });

      if (response.ok) {
        setSuccess("Invitation cancelled");
        fetchData();
      } else {
        setError("Failed to cancel invitation");
      }
    } catch (error) {
      setError("Network error");
    }
  };

  // Blog handlers
  const generateSlug = (title: string) => {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/(^-|-$)/g, "");
  };

  const openBlogDialog = (blog?: Blog) => {
    if (blog) {
      setEditingBlog(blog);
      setBlogForm({
        title: blog.title,
        slug: blog.slug,
        excerpt: blog.excerpt,
        content: blog.content || "",
        category: blog.category,
        author: blog.author,
        readTime: blog.readTime,
        image: blog.image || "",
        featured: blog.featured,
        published: blog.published,
      });
    } else {
      setEditingBlog(null);
      setBlogForm({
        title: "",
        slug: "",
        excerpt: "",
        content: "",
        category: "",
        author: "",
        readTime: "5 min read",
        image: "",
        featured: false,
        published: true,
      });
    }
    setBlogDialogOpen(true);
  };

  const handleSaveBlog = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      const url = editingBlog
        ? `/api/admin/blogs/${editingBlog.id}`
        : "/api/admin/blogs";
      const method = editingBlog ? "PUT" : "POST";

      const response = await authFetch(url, {
        method,
        body: JSON.stringify(blogForm),
      });

      if (response.ok) {
        setSuccess(editingBlog ? "Blog updated" : "Blog created");
        setBlogDialogOpen(false);
        fetchData();
      } else {
        const data = await response.json();
        setError(data.message || "Failed to save blog");
      }
    } catch (error) {
      setError("Network error");
    }
  };

  const handleDeleteBlog = async (blogId: string) => {
    if (!confirm("Are you sure you want to delete this blog?")) return;

    try {
      const response = await authFetch(`/api/admin/blogs/${blogId}`, { method: "DELETE" });

      if (response.ok) {
        setSuccess("Blog deleted");
        fetchData();
      } else {
        setError("Failed to delete blog");
      }
    } catch (error) {
      setError("Network error");
    }
  };

  // ATO Alert handlers
  const openAlertDialog = (alert?: AtoAlert) => {
    if (alert) {
      setEditingAlert(alert);
      setAlertForm({
        title: alert.title,
        type: alert.type,
        link: alert.link,
        active: alert.active,
        priority: alert.priority,
      });
    } else {
      setEditingAlert(null);
      setAlertForm({
        title: "",
        type: "update",
        link: "",
        active: true,
        priority: 0,
      });
    }
    setAlertDialogOpen(true);
  };

  const handleSaveAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      const url = editingAlert
        ? `/api/admin/ato-alerts/${editingAlert.id}`
        : "/api/admin/ato-alerts";
      const method = editingAlert ? "PUT" : "POST";

      const response = await authFetch(url, {
        method,
        body: JSON.stringify(alertForm),
      });

      if (response.ok) {
        setSuccess(editingAlert ? "Alert updated" : "Alert created");
        setAlertDialogOpen(false);
        fetchData();
      } else {
        const data = await response.json();
        setError(data.message || "Failed to save alert");
      }
    } catch (error) {
      setError("Network error");
    }
  };

  const handleDeleteAlert = async (alertId: string) => {
    if (!confirm("Are you sure you want to delete this alert?")) return;

    try {
      const response = await authFetch(`/api/admin/ato-alerts/${alertId}`, { method: "DELETE" });

      if (response.ok) {
        setSuccess("Alert deleted");
        fetchData();
      } else {
        setError("Failed to delete alert");
      }
    } catch (error) {
      setError("Network error");
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-AU", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "approved":
        return <Badge className="bg-green-100 text-green-800">Approved</Badge>;
      case "pending":
        return <Badge className="bg-yellow-100 text-yellow-800">Pending</Badge>;
      case "rejected":
        return <Badge className="bg-red-100 text-red-800">Rejected</Badge>;
      case "suspended":
        return <Badge className="bg-gray-100 text-gray-800">Suspended</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-50 via-white to-blue-50/30">
      <Navbar />

      <main className="flex-1 pt-32 pb-20">
        <div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
            <div className="flex items-center gap-4">
              <Link href="/dashboard">
                <Button variant="ghost" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back
                </Button>
              </Link>
              <div>
                <h1 className="text-3xl font-bold flex items-center gap-3">
                  <Shield className="h-8 w-8 text-primary" />
                  Admin Panel
                </h1>
                <p className="text-muted-foreground">
                  Manage users, approvals, and invitations
                </p>
              </div>
            </div>

            <Dialog open={inviteDialogOpen} onOpenChange={setInviteDialogOpen}>
              <DialogTrigger asChild>
                <Button className="mt-4 md:mt-0">
                  <UserPlus className="h-4 w-4 mr-2" />
                  Invite User
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Invite New User</DialogTitle>
                  <DialogDescription>
                    Send an invitation email to a new user or accountant
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleInvite} className="space-y-4 mt-4">
                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address</Label>
                    <Input
                      id="email"
                      type="email"
                      value={inviteEmail}
                      onChange={(e) => setInviteEmail(e.target.value)}
                      placeholder="user@example.com"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="role">Role</Label>
                    <Select value={inviteRole} onValueChange={(v) => setInviteRole(v as "user" | "accountant")}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="user">User</SelectItem>
                        <SelectItem value="accountant">Accountant</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button type="submit" className="w-full" disabled={isInviting}>
                    {isInviting ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Sending...
                      </>
                    ) : (
                      <>
                        <Mail className="h-4 w-4 mr-2" />
                        Send Invitation
                      </>
                    )}
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          {error && (
            <Alert variant="destructive" className="mb-6">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {success && (
            <Alert className="mb-6 border-green-200 bg-green-50 text-green-800">
              <AlertDescription>{success}</AlertDescription>
            </Alert>
          )}

          {/* Stats */}
          <div className="grid md:grid-cols-4 gap-4 mb-8">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Total Users</p>
                    <p className="text-3xl font-bold">{users.length}</p>
                  </div>
                  <Users className="h-8 w-8 text-muted-foreground" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Pending Approvals</p>
                    <p className="text-3xl font-bold text-yellow-600">{pendingUsers.length}</p>
                  </div>
                  <Clock className="h-8 w-8 text-yellow-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Open Invitations</p>
                    <p className="text-3xl font-bold text-blue-600">{invitations.length}</p>
                  </div>
                  <Mail className="h-8 w-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Accountants</p>
                    <p className="text-3xl font-bold text-purple-600">
                      {users.filter((u) => u.role === "accountant").length}
                    </p>
                  </div>
                  <Shield className="h-8 w-8 text-purple-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Tabs */}
          <Tabs defaultValue="pending" className="space-y-4">
            <TabsList className="flex-wrap h-auto gap-1">
              <TabsTrigger value="pending" className="flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Pending ({pendingUsers.length})
              </TabsTrigger>
              <TabsTrigger value="users" className="flex items-center gap-2">
                <Users className="h-4 w-4" />
                All Users
              </TabsTrigger>
              <TabsTrigger value="invitations" className="flex items-center gap-2">
                <Mail className="h-4 w-4" />
                Invitations
              </TabsTrigger>
              <TabsTrigger value="blogs" className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Blogs ({blogs.length})
              </TabsTrigger>
              <TabsTrigger value="alerts" className="flex items-center gap-2">
                <Bell className="h-4 w-4" />
                ATO Alerts ({atoAlerts.length})
              </TabsTrigger>
            </TabsList>

            {/* Pending Approvals */}
            <TabsContent value="pending">
              <Card>
                <CardHeader>
                  <CardTitle>Pending Registrations</CardTitle>
                  <CardDescription>Users waiting for your approval</CardDescription>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <div className="flex justify-center py-8">
                      <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                    </div>
                  ) : pendingUsers.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      No pending registrations
                    </div>
                  ) : (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Name</TableHead>
                          <TableHead>Email</TableHead>
                          <TableHead>Phone</TableHead>
                          <TableHead>Registered</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {pendingUsers.map((u) => (
                          <TableRow key={u.id}>
                            <TableCell className="font-medium">
                              {u.firstName} {u.lastName}
                            </TableCell>
                            <TableCell>{u.email}</TableCell>
                            <TableCell>{u.phone || "-"}</TableCell>
                            <TableCell>{formatDate(u.createdAt)}</TableCell>
                            <TableCell className="text-right">
                              <div className="flex justify-end gap-2">
                                <Button
                                  size="sm"
                                  onClick={() => handleApprove(u.id)}
                                  className="bg-green-600 hover:bg-green-700"
                                >
                                  <CheckCircle className="h-4 w-4 mr-1" />
                                  Approve
                                </Button>
                                <Button
                                  size="sm"
                                  variant="destructive"
                                  onClick={() => handleReject(u.id)}
                                >
                                  <XCircle className="h-4 w-4 mr-1" />
                                  Reject
                                </Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* All Users */}
            <TabsContent value="users">
              <Card>
                <CardHeader>
                  <CardTitle>All Users</CardTitle>
                  <CardDescription>Manage all registered users</CardDescription>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <div className="flex justify-center py-8">
                      <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                    </div>
                  ) : (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Name</TableHead>
                          <TableHead>Email</TableHead>
                          <TableHead>Role</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Last Login</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {users.map((u) => (
                          <TableRow key={u.id}>
                            <TableCell className="font-medium">
                              {u.firstName} {u.lastName}
                            </TableCell>
                            <TableCell>{u.email}</TableCell>
                            <TableCell className="capitalize">{u.role}</TableCell>
                            <TableCell>{getStatusBadge(u.status)}</TableCell>
                            <TableCell>
                              {u.lastLoginAt ? formatDate(u.lastLoginAt) : "Never"}
                            </TableCell>
                            <TableCell className="text-right">
                              {u.id !== user?.id && u.role !== "admin" && (
                                u.status === "suspended" ? (
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => handleReactivate(u.id)}
                                  >
                                    Reactivate
                                  </Button>
                                ) : u.status === "approved" ? (
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    className="text-red-600"
                                    onClick={() => handleSuspend(u.id)}
                                  >
                                    Suspend
                                  </Button>
                                ) : null
                              )}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Invitations */}
            <TabsContent value="invitations">
              <Card>
                <CardHeader>
                  <CardTitle>Pending Invitations</CardTitle>
                  <CardDescription>Invitations waiting to be accepted</CardDescription>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <div className="flex justify-center py-8">
                      <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                    </div>
                  ) : invitations.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      No pending invitations
                    </div>
                  ) : (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Email</TableHead>
                          <TableHead>Role</TableHead>
                          <TableHead>Sent</TableHead>
                          <TableHead>Expires</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {invitations.map((inv) => (
                          <TableRow key={inv.id}>
                            <TableCell className="font-medium">{inv.email}</TableCell>
                            <TableCell className="capitalize">{inv.role}</TableCell>
                            <TableCell>{formatDate(inv.createdAt)}</TableCell>
                            <TableCell>{formatDate(inv.expiresAt)}</TableCell>
                            <TableCell className="text-right">
                              <Button
                                size="sm"
                                variant="ghost"
                                className="text-red-600"
                                onClick={() => handleCancelInvitation(inv.id)}
                              >
                                Cancel
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* Blogs */}
            <TabsContent value="blogs">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <div>
                    <CardTitle>Blog Posts</CardTitle>
                    <CardDescription>Manage blog articles for your website</CardDescription>
                  </div>
                  <Button onClick={() => openBlogDialog()}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Blog
                  </Button>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <div className="flex justify-center py-8">
                      <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                    </div>
                  ) : blogs.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      No blog posts yet
                    </div>
                  ) : (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Title</TableHead>
                          <TableHead>Category</TableHead>
                          <TableHead>Author</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Created</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {blogs.map((blog) => (
                          <TableRow key={blog.id}>
                            <TableCell className="font-medium">
                              <div className="flex items-center gap-2">
                                {blog.title}
                                {blog.featured && (
                                  <Badge className="bg-yellow-100 text-yellow-800">Featured</Badge>
                                )}
                              </div>
                            </TableCell>
                            <TableCell>{blog.category}</TableCell>
                            <TableCell>{blog.author}</TableCell>
                            <TableCell>
                              {blog.published ? (
                                <Badge className="bg-green-100 text-green-800">Published</Badge>
                              ) : (
                                <Badge className="bg-gray-100 text-gray-800">Draft</Badge>
                              )}
                            </TableCell>
                            <TableCell>{formatDate(blog.createdAt)}</TableCell>
                            <TableCell className="text-right">
                              <div className="flex justify-end gap-2">
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => openBlogDialog(blog)}
                                >
                                  <Pencil className="h-4 w-4" />
                                </Button>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  className="text-red-600"
                                  onClick={() => handleDeleteBlog(blog.id)}
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            {/* ATO Alerts */}
            <TabsContent value="alerts">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <div>
                    <CardTitle>ATO Alerts</CardTitle>
                    <CardDescription>Manage ATO updates and alerts for your website</CardDescription>
                  </div>
                  <Button onClick={() => openAlertDialog()}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Alert
                  </Button>
                </CardHeader>
                <CardContent>
                  {isLoading ? (
                    <div className="flex justify-center py-8">
                      <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                    </div>
                  ) : atoAlerts.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      No ATO alerts yet
                    </div>
                  ) : (
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Title</TableHead>
                          <TableHead>Type</TableHead>
                          <TableHead>Priority</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {atoAlerts.map((alert) => (
                          <TableRow key={alert.id}>
                            <TableCell className="font-medium max-w-md truncate">
                              {alert.title}
                            </TableCell>
                            <TableCell>
                              <Badge
                                className={
                                  alert.type === "alert"
                                    ? "bg-red-100 text-red-800"
                                    : alert.type === "update"
                                    ? "bg-blue-100 text-blue-800"
                                    : "bg-yellow-100 text-yellow-800"
                                }
                              >
                                {alert.type}
                              </Badge>
                            </TableCell>
                            <TableCell>{alert.priority}</TableCell>
                            <TableCell>
                              {alert.active ? (
                                <Badge className="bg-green-100 text-green-800">Active</Badge>
                              ) : (
                                <Badge className="bg-gray-100 text-gray-800">Inactive</Badge>
                              )}
                            </TableCell>
                            <TableCell className="text-right">
                              <div className="flex justify-end gap-2">
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => openAlertDialog(alert)}
                                >
                                  <Pencil className="h-4 w-4" />
                                </Button>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  className="text-red-600"
                                  onClick={() => handleDeleteAlert(alert.id)}
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Blog Dialog */}
          <Dialog open={blogDialogOpen} onOpenChange={setBlogDialogOpen}>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>{editingBlog ? "Edit Blog" : "Create Blog"}</DialogTitle>
                <DialogDescription>
                  {editingBlog ? "Update the blog post details" : "Create a new blog post"}
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSaveBlog} className="space-y-4 mt-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="blog-title">Title</Label>
                    <Input
                      id="blog-title"
                      value={blogForm.title}
                      onChange={(e) => {
                        setBlogForm({
                          ...blogForm,
                          title: e.target.value,
                          slug: blogForm.slug || generateSlug(e.target.value),
                        });
                      }}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="blog-slug">Slug</Label>
                    <Input
                      id="blog-slug"
                      value={blogForm.slug}
                      onChange={(e) => setBlogForm({ ...blogForm, slug: e.target.value })}
                      required
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="blog-excerpt">Excerpt</Label>
                  <Textarea
                    id="blog-excerpt"
                    value={blogForm.excerpt}
                    onChange={(e) => setBlogForm({ ...blogForm, excerpt: e.target.value })}
                    rows={2}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="blog-content">Content</Label>
                  <Textarea
                    id="blog-content"
                    value={blogForm.content}
                    onChange={(e) => setBlogForm({ ...blogForm, content: e.target.value })}
                    rows={6}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="blog-category">Category</Label>
                    <Input
                      id="blog-category"
                      value={blogForm.category}
                      onChange={(e) => setBlogForm({ ...blogForm, category: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="blog-author">Author</Label>
                    <Input
                      id="blog-author"
                      value={blogForm.author}
                      onChange={(e) => setBlogForm({ ...blogForm, author: e.target.value })}
                      required
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="blog-readTime">Read Time</Label>
                    <Input
                      id="blog-readTime"
                      value={blogForm.readTime}
                      onChange={(e) => setBlogForm({ ...blogForm, readTime: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="blog-image">Image URL</Label>
                    <Input
                      id="blog-image"
                      value={blogForm.image}
                      onChange={(e) => setBlogForm({ ...blogForm, image: e.target.value })}
                    />
                  </div>
                </div>
                <div className="flex items-center gap-6">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={blogForm.featured}
                      onChange={(e) => setBlogForm({ ...blogForm, featured: e.target.checked })}
                      className="rounded"
                    />
                    <span>Featured</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={blogForm.published}
                      onChange={(e) => setBlogForm({ ...blogForm, published: e.target.checked })}
                      className="rounded"
                    />
                    <span>Published</span>
                  </label>
                </div>
                <Button type="submit" className="w-full">
                  {editingBlog ? "Update Blog" : "Create Blog"}
                </Button>
              </form>
            </DialogContent>
          </Dialog>

          {/* ATO Alert Dialog */}
          <Dialog open={alertDialogOpen} onOpenChange={setAlertDialogOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{editingAlert ? "Edit Alert" : "Create Alert"}</DialogTitle>
                <DialogDescription>
                  {editingAlert ? "Update the ATO alert details" : "Create a new ATO alert"}
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSaveAlert} className="space-y-4 mt-4">
                <div className="space-y-2">
                  <Label htmlFor="alert-title">Title</Label>
                  <Textarea
                    id="alert-title"
                    value={alertForm.title}
                    onChange={(e) => setAlertForm({ ...alertForm, title: e.target.value })}
                    rows={2}
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="alert-type">Type</Label>
                    <Select
                      value={alertForm.type}
                      onValueChange={(v) =>
                        setAlertForm({ ...alertForm, type: v as "update" | "alert" | "reminder" })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="update">Update</SelectItem>
                        <SelectItem value="alert">Alert</SelectItem>
                        <SelectItem value="reminder">Reminder</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="alert-priority">Priority</Label>
                    <Input
                      id="alert-priority"
                      type="number"
                      value={alertForm.priority}
                      onChange={(e) =>
                        setAlertForm({ ...alertForm, priority: parseInt(e.target.value) || 0 })
                      }
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="alert-link">Link URL</Label>
                  <Input
                    id="alert-link"
                    value={alertForm.link}
                    onChange={(e) => setAlertForm({ ...alertForm, link: e.target.value })}
                    placeholder="https://www.ato.gov.au/..."
                    required
                  />
                </div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={alertForm.active}
                    onChange={(e) => setAlertForm({ ...alertForm, active: e.target.checked })}
                    className="rounded"
                  />
                  <span>Active</span>
                </label>
                <Button type="submit" className="w-full">
                  {editingAlert ? "Update Alert" : "Create Alert"}
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </main>

      <Footer />
    </div>
  );
}
