export type User = { id: string; tenantId: string; role: "admin" | "member" };
export type Project = { id: string; tenantId: string; ownerId: string };

export function canEditProject(user: User, project: Project): boolean {
  return user.role === "admin" || project.ownerId === user.id;
}
